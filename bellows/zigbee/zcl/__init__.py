import asyncio
import logging

import bellows.types as t
from . import foundation


LOGGER = logging.getLogger(__name__)


def deserialize(aps_frame, data):
    frame_control, data = data[0], data[1:]
    frame_type = frame_control & 0b0011
    direction = (frame_control & 0b1000) >> 3
    if frame_control & 0b0100:
        # Manufacturer specific value present
        data = data[2:]
    tsn, command_id, data = data[0], data[1], data[2:]

    is_reply = bool(direction)

    if frame_type == 1:
        # Cluster command
        if aps_frame.clusterId not in Cluster._registry:
            LOGGER.warning("Ignoring unknown cluster ID 0x%04x",
                           aps_frame.clusterId)
            return tsn, command_id + 256, is_reply, data
        cluster = Cluster._registry[aps_frame.clusterId]
        # Cluster-specific command

        if direction:
            commands = cluster.client_commands
        else:
            commands = cluster.server_commands

        try:
            schema = commands[command_id][1]
            is_reply = commands[command_id][2]
        except KeyError:
            LOGGER.warning("Unknown cluster-specific command %s", command_id)
            return tsn, command_id + 256, is_reply, data

        # Bad hack to differentiate foundation vs cluster
        command_id = command_id + 256
    else:
        # General command
        try:
            schema = foundation.COMMANDS[command_id][1]
            is_reply = foundation.COMMANDS[command_id][2]
        except KeyError:
            LOGGER.warning("Unknown foundation command %s", command_id)
            return tsn, command_id, is_reply, data

    value, data = t.deserialize(data, schema)
    if data != b'':
        # TODO: Seems sane to check, but what should we do?
        LOGGER.warning("Data remains after deserializing ZCL frame")

    return tsn, command_id, is_reply, value


class Registry(type):
    def __init__(cls, name, bases, nmspc):
        super(Registry, cls).__init__(name, bases, nmspc)
        if hasattr(cls, 'cluster_id'):
            cls._registry[cls.cluster_id] = cls


class Cluster(metaclass=Registry):
    """A cluster on an endpoint"""
    _registry = {}

    def __init__(self, endpoint):
        self._endpoint = endpoint
        self._attr_cache = {}

    @classmethod
    def from_id(cls, endpoint, cluster_id):
        try:
            return cls._registry[cluster_id](endpoint)
        except KeyError:
            LOGGER.warning("Unknown cluster %s", cluster_id)
            c = cls(endpoint)
            c.cluster_id = cluster_id
            return c

    def request(self, general, command_id, schema, *args):
        aps = self._endpoint.get_aps(self.cluster_id)
        if general:
            frame_control = 0x00
        else:
            frame_control = 0x01
        data = bytes([frame_control, aps.sequence, command_id])
        data += t.serialize(args, schema)

        return self._endpoint._device.request(aps, data)

    def handle_request(self, aps_frame, tsn, command_id, args):
        if command_id == 0x0a:  # Report attributes
            valuestr = ", ".join([
                "%s=%s" % (a.attrid, a.value.value) for a in args[0]
            ])
            self.debug("Attribute report received: %s", valuestr)
            for attr in args[0]:
                self._attr_cache[attr.attrid] = attr.value.value
        elif command_id > 0xff:
            # Unencapsulate bad hack
            command_id -= 256
            self.handle_cluster_request(aps_frame, tsn, command_id, args)
        else:
            self.warn("No handler for general command %s", command_id)

    def handle_cluster_request(self, aps_frame, tsn, command_id, args):
        self.warn("No handler for cluster command %s", command_id)

    @asyncio.coroutine
    def read_attributes(self, attributes):
        schema = foundation.COMMANDS[0x00][1]
        attributes = [t.uint16_t(a) for a in attributes]
        v = yield from self.request(True, 0x00, schema, attributes)
        for record in v[0]:
            if record.status == 0:
                self._attr_cache[record.attrid] = record.value.value
        return v

    def write_attributes(self, attributes):
        args = []
        for attrid, value in attributes.items():
            a = foundation.Attribute()
            a.attrid = t.uint16_t(attrid)
            a.value = foundation.TypeValue()
            python_type = self.attributes[attrid][1]
            a.value.type = t.uint8_t(foundation.DATA_TYPE_IDX[python_type])
            a.value.value = python_type(value)
            args.append(a)
        schema = foundation.COMMANDS[0x02][1]
        return self.request(True, 0x02, schema, args)

    def bind(self):
        return self._endpoint._device.zdo.bind(self._endpoint._endpoint_id, self.cluster_id)

    def unbind(self):
        return self._endpoint._device.zdo.unbind(self._endpoint._endpoint_id, self.cluster_id)

    def configure_reporting(self, attribute, min_interval, max_interval, reportable_change):
        schema = foundation.COMMANDS[0x06][1]
        cfg = foundation.AttributeReportingConfig()
        cfg.direction = 0
        cfg.attrid = attribute
        cfg.datatype = foundation.DATA_TYPE_IDX.get(
            self.attributes.get(attribute, (None, None))[1],
            None)
        cfg.min_interval = min_interval
        cfg.max_interval = max_interval
        cfg.reportable_change = reportable_change
        return self.request(True, 0x06, schema, [cfg])

    def command(self, command, *args):
        schema = self.server_commands[command][1]
        return self.request(False, command, schema, *args)

    @property
    def name(self):
        return self.__class__.__name__

    def log(self, lvl, msg, *args):
        msg = '[0x%04x:%s:0x%04x] ' + msg
        args = (
            self._endpoint._device._nwk,
            self._endpoint._endpoint_id,
            self.cluster_id,
        ) + args
        return LOGGER.log(lvl, msg, *args)

    def debug(self, msg, *args):
        return self.log(logging.DEBUG, msg, *args)

    def info(self, msg, *args):
        return self.log(logging.INFO, msg, *args)

    def warn(self, msg, *args):
        return self.log(logging.WARNING, msg, *args)

    def error(self, msg, *args):
        return self.log(logging.ERROR, msg, *args)

# Import to populate the registry
from . import clusters
