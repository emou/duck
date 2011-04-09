"""
A simple test runner which looks for tests in all subdirectories and
executes them.
"""
import logging
import os
import subprocess
import sys
import unittest

_TEST_SUFFIX='Test.py'
_LOGGER_NAME='test'
_DEFAULT_LOGGING_LEVEL=logging.INFO
_DEFAULT_LOGGING_HANDLER=logging.StreamHandler(sys.stdout)

class TestsExecutor(object):

    def run(self):
        logger = logging.getLogger(_LOGGER_NAME)
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(_DEFAULT_LOGGING_LEVEL)

        if 'PYTHONPATH' in os.environ:
            logger.warning('Warning: PYTHONPATH will be replaced with the root'
                           ' directory of the project.')
        os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
        for (root, dirs, files) in os.walk(os.getcwd()):
            for f in files:
                if f.endswith(_TEST_SUFFIX):
                    logger.info('Running test %s' % f)
                    ret = subprocess.call([sys.executable, '-tt', os.path.join(root, f)])
                    if ret != 0:
                        logger.info('\n====== TESTS FAILED. ======')
                        return ret
        return 0

if __name__ == '__main__':
    sys.exit(TestsExecutor().run())
