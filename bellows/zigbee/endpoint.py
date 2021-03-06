import asyncio
import enum
import logging

from bellows.zigbee import zcl, zha


LOGGER = logging.getLogger(__name__)


class Status(enum.IntEnum):
    """The status of an Endpoint"""
    # No initialization is done
    NEW = 0
    # Endpoint information (device type, clusters, etc) init done
    ZDO_INIT = 1


class Endpoint:
    """An endpoint on a device on the network"""
    def __init__(self, device, endpoint_id):
        self._device = device
        self._endpoint_id = endpoint_id
        self.clusters = {}
        self.status = Status.NEW

    @asyncio.coroutine
    def initialize(self):
        self.info("Discovering endpoint information")
        sdr = yield from self._device.zdo.request(
            0x0004,
            self._device._nwk,
            self._endpoint_id,
        )
        if sdr[0] != 0:
            # TODO: Handle
            self.warn("Failed ZDO request during device initialization")
            return

        self.info("Discovered endpoint information: %s", sdr[2])

        sd = sdr[2]
        self.profile_id = sd.profile
        self.device_type = sd.device_type
        if self.profile_id == 260:
            try:
                self.device_type = zha.DeviceType(self.device_type)
            except:
                pass

        for cluster in sd.input_clusters:
            self.add_cluster(cluster)

        self.output_clusters = sd.output_clusters

        self.status = Status.ZDO_INIT

    def add_cluster(self, cluster_id):
        """Adds a device's input cluster

        (a server cluster supported by the device)
        """
        cluster = zcl.Cluster.from_id(self, cluster_id)
        self.clusters[cluster_id] = cluster
        return cluster

    def get_aps(self, cluster):
        assert self.status != Status.NEW
        return self._device.get_aps(
            profile=self.profile_id,
            cluster=cluster,
            endpoint=self._endpoint_id,
        )

    def handle_request(self, aps_frame, tsn, command_id, args):
        try:
            self.clusters[aps_frame.clusterId].handle_request(aps_frame, tsn, command_id, args)
        except KeyError:
            self.warn("Request on unknown cluster 0x%04x", aps_frame.clusterId)

    def log(self, lvl, msg, *args):
        msg = '[0x%04x:%s] ' + msg
        args = (self._device._nwk, self._endpoint_id) + args
        return LOGGER.log(lvl, msg, *args)

    def debug(self, msg, *args):
        return self.log(logging.DEBUG, msg, *args)

    def info(self, msg, *args):
        return self.log(logging.INFO, msg, *args)

    def warn(self, msg, *args):
        return self.log(logging.WARNING, msg, *args)

    def error(self, msg, *args):
        return self.log(logging.ERROR, msg, *args)
