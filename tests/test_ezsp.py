import asyncio
import functools
from unittest import mock

import pytest

from bellows import ezsp, uart


@pytest.fixture
def ezsp_f():
    return ezsp.EZSP()


def test_connect(ezsp_f, monkeypatch):
    connected = False

    @asyncio.coroutine
    def mockconnect(*args, **kwargs):
        nonlocal connected
        connected = True

    monkeypatch.setattr(uart, 'connect', mockconnect)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(ezsp_f.connect(None))
    assert connected


def test_reset(ezsp_f):
    ezsp_f._gw = mock.MagicMock()
    ezsp_f.reset()
    assert ezsp_f._gw.reset.call_count == 1


def test_close(ezsp_f):
    ezsp_f._gw = mock.MagicMock()
    ezsp_f.close()
    assert ezsp_f._gw.close.call_count == 1


def test_attr(ezsp_f):
    m = ezsp_f.version
    assert isinstance(m, functools.partial)
    assert callable(m)


def test_non_existent_attr(ezsp_f):
    with pytest.raises(AttributeError):
        ezsp_f.nonexistentMethod()


def test_command(ezsp_f):
    ezsp_f._gw = mock.MagicMock()
    ezsp_f._command('version')
    assert ezsp_f._gw.data.call_count == 1


def _test_list_command(ezsp_f, mockcommand):
    loop = asyncio.get_event_loop()
    ezsp_f._command = mockcommand
    return loop.run_until_complete(ezsp_f._list_command(
        'startScan',
        ['networkFoundHandler'],
        'scanCompleteHandler',
        1,
    ))


def test_list_command(ezsp_f):
    @asyncio.coroutine
    def mockcommand(name, *args):
        assert name == 'startScan'
        ezsp_f.frame_received(b'\x01\x00\x1b')
        ezsp_f.frame_received(b'\x02\x00\x1b')
        ezsp_f.frame_received(b'\x03\x00\x1c')

        return [0]

    result = _test_list_command(ezsp_f, mockcommand)
    assert len(result) == 2


def test_list_command_initial_failure(ezsp_f):
    @asyncio.coroutine
    def mockcommand(name, *args):
        assert name == 'startScan'
        return [1]

    with pytest.raises(Exception):
        _test_list_command(ezsp_f, mockcommand)


def test_list_command_later_failure(ezsp_f):
    @asyncio.coroutine
    def mockcommand(name, *args):
        assert name == 'startScan'
        ezsp_f.frame_received(b'\x01\x00\x1b')
        ezsp_f.frame_received(b'\x02\x00\x1b')
        ezsp_f.frame_received(b'\x03\x00\x1c\x01\x01')

        return [0]

    with pytest.raises(Exception):
        _test_list_command(ezsp_f, mockcommand)


def test_receive_new(ezsp_f):
    ezsp_f.handle_callback = mock.MagicMock()
    ezsp_f.frame_received(b'\x00\xff\x00\x04\x05\x06')
    assert ezsp_f.handle_callback.call_count == 1


def test_receive_reply(ezsp_f):
    ezsp_f.handle_callback = mock.MagicMock()
    callback_mock = mock.MagicMock()
    ezsp_f._awaiting[0] = (0, ezsp_f.COMMANDS['version'][2], callback_mock)
    ezsp_f.frame_received(b'\x00\xff\x00\x04\x05\x06')

    assert 0 not in ezsp_f._awaiting
    assert callback_mock.set_result.called_once_with([4, 5, 6])
    assert ezsp_f.handle_callback.call_count == 0


def test_callback(ezsp_f):
    testcb = mock.MagicMock()

    cbid = ezsp_f.add_callback(testcb)
    ezsp_f.handle_callback(1, 2, 3)

    assert testcb.call_count == 1

    ezsp_f.remove_callback(cbid)
    ezsp_f.handle_callback(4, 5, 6)
    assert testcb.call_count == 1


def test_callback_multi(ezsp_f):
    testcb = mock.MagicMock()

    cbid1 = ezsp_f.add_callback(testcb)
    ezsp_f.add_callback(testcb)

    ezsp_f.handle_callback(1, 2, 3)

    assert testcb.call_count == 2

    ezsp_f.remove_callback(cbid1)

    ezsp_f.handle_callback(4, 5, 6)
    testcb.assert_has_calls([
         mock.call(1, 2, 3),
         mock.call(1, 2, 3),
         mock.call(4, 5, 6),
    ])


def test_callback_exc(ezsp_f):
    testcb = mock.MagicMock()
    testcb.side_effect = Exception("Testing")

    ezsp_f.add_callback(testcb)
    ezsp_f.handle_callback(1)
    assert testcb.call_count == 1
