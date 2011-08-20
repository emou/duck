import mpd
import threading
import unittest

_TMP_FILE='test_file'

class MPDClientMock(object):

    class ClientError(Exception):
        pass

    def __init__(self):
        self.connected = False
        self.idle = False

    def connect(self, host, port):
        self.host = host
        self.port = port
        self.connected = True

        self._file = open(_TMP_FILE, 'w')
        self._file.truncate(0)
        self._file_read = open(_TMP_FILE, 'r')

    def close(self):
        pass
    
    def disconnect(self):
        self.connected = False
    
    def fileno(self):
        return self._file.fileno()
    
    def send_idle(self):
        if self.idle:
            raise self.ClientError('Tried to send idle while idle.')
        self.idle = True
    
    def send_noidle(self):
        if not self.idle:
            raise self.ClientError('Tried to send noidle while noidle.')
        self.idle = False
    
    def fetch_idle(self):
        self._file_read.readline()
        return ['playlist']

    def _make_ready(self):
        self._file.write('Foo\n')
    
    def __del__(self):
        self._file.close()
        self._file_read.close()

mpd.MPDClient = MPDClientMock

class FrontendMock(object):
    def __init__(self):
        self.last_changes = None
        self.async_refresh_called = threading.Event()
        self.async_refresh_called.clear()

    def async_refresh(self, changes=None):
        self.async_refresh_called.set()

from duck.backend.mpd import Backend
class TestCase(unittest.TestCase):

    def setUp(self):
        self.backend = Backend(FrontendMock())

    def test_exception_when_not_initialized(self):
        """
        The backend should raise an AttributeError saying there's no 'client'
        attribute. This might be changed to something better later on, but for
        now at least have a test.
        """
        self.assertRaises(AttributeError, self.backend.idle)
        self.backend.initialize()
        self.assertTrue(hasattr(self.backend, 'client'))
        self.backend.disconnect()
    
    def test_idle_thread_runs_after_initialize(self):
        self.backend.initialize()
        self.assertTrue(self.backend.idle_thread.frontend is not None)
        self.assertTrue(self.backend.idle_thread.is_alive())
        self.assertTrue(self.backend.idle_thread.should_run)
        self.assertTrue(self.backend.idle_thread.daemon)
        self.backend.disconnect()
 
    def test_go_into_idle_mode(self):
        self.backend.initialize()
        self.assertFalse(self.backend.client.idle)
        self.assertFalse(self.backend.idle_request.is_set())
        self.backend.idle()
        self.assertTrue(self.backend.client.idle)
        self.assertTrue(self.backend.idle_request.is_set())
        # If this test hangs, async_refresh is never called!
        self.assertTrue(self.backend.frontend.async_refresh_called.wait(5.0))
        self.backend.frontend.async_refresh_called.clear()

    def test_with_statement(self):
        self.backend.initialize()
        self.backend.idle()
        with self.backend:
            pass
        self.assertEqual(self.backend.last_changes(), ['playlist'])

if __name__ == '__main__':
    unittest.main()
