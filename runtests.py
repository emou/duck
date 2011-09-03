"""
A simple test runner which looks for tests in all subdirectories and
executes them.
"""
import argparse
import logging
import os
import re
import subprocess
import sys

_TEST_SUFFIX='Test.py'
_LOGGER_NAME='test'
_DEFAULT_LOGGING_LEVEL=logging.INFO
_DEFAULT_LOGGING_HANDLER=logging.StreamHandler(sys.stdout)

class TestsExecutor(object):

    def __init__(self, args):
        self.args = args
    
    def _match_test(self, test_path, patterns):
        """
        Tries to match `test_path` of test module against `patterns`, which
        must've been passed on the command line.
        """
        return test_path in patterns or \
               any(test_path.endswith(p) for p in patterns) or \
               any(re.match(p, test_path) for p in patterns)

    def run(self):
        logger = logging.getLogger(_LOGGER_NAME)
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(_DEFAULT_LOGGING_LEVEL)

        if 'PYTHONPATH' in os.environ:
            logger.warning('Warning: PYTHONPATH will be replaced with the root'
                           ' directory of the project.')
        os.environ['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))

        tests = []
        for (root, dirs, files) in os.walk(os.getcwd()):
            for f in files:
                if f.endswith(_TEST_SUFFIX):
                    tests.append(os.path.join(root, f))
        if self.args.tests:
            tests = filter(
                lambda t: self._match_test(t, self.args.tests),
                tests
            )

        for f in tests:
            logger.info('Running %s' % f)
            p = subprocess.Popen([sys.executable, '-tt', f],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            (out, err) = p.communicate()
            if out:
                logger.info(out)
            if err:
                # Regular test output from the TextTestRunner goes to stderr,
                # but this is info for us.
                logger.info(err)
            if p.returncode != 0:
                return p.returncode
        return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Duck tests. Stop on first failed test module.')
    parser.add_argument('tests', metavar='T', type=str, nargs='*',
                        help='Run only the specified tests. You can specify regular expression patterns.')
    args = parser.parse_args()
    sys.exit(TestsExecutor(args).run())
