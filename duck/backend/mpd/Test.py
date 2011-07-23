import duck
import mpd
import os
import unittest

_TMP_FILE='test_file'

class MPDClientMock(object):

    def __init__(self):
        self.connected = False
        self.idle = False

    def connect(self, host, port):
        self.host = host
        self.port = port
        self.connected = True

        self._file = open(_TMP_FILE, 'w')
        self._file.truncate(0)

    def close(self):
        pass
    
    def disconnect(self):
        self.connected = False
    
    def fileno(self):
        return self._file.fileno()
    
    def send_idle(self):
        self.idle = True
    
    def fetch_idle(self):
        self._file.readline()
        return ['playlist']

    def _make_ready(self):
        self._file.write('Foo\n')
    
    def __del__(self):
        self._file.close()

mpd.MPDClient = MPDClientMock

class FrontendMock(object):
    def __init__(self):
        self.last_changes = None

    def async_refresh(self, changes=None):
        self.last_changes = changes

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
    
    def test_idle(self):
        self.backend.initialize()
        self.assertFalse(self.backend.client.idle)
        self.backend.idle()
        self.assertTrue(self.backend.client.idle)
        self.backend.client._make_ready()

if __name__ == '__main__':
    unittest.main()
