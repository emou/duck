import unittest
import duck
from duck.backend.mpd import Backend

class TestCase(unittest.TestCase):

    def setUp(self):
        self.backend = Backend()
    
    def tearDown(self):
        self.backend.disconnect()
        self.backend = None

    def test_backend(self):
        import select
        self.backend.client.send_idle()
        select.select([self.backend.client], [], [])
        print self.backend.client.fetch_idle()

if __name__ == '__main__':
    unittest.main()
