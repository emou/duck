#!/usr/bin/env python
import sys
from os.path import dirname, abspath

sys.path.append(dirname(abspath(__file__)))
from duck.frontend.wxwidgets import Frontend
from duck.backend.mpd import Backend
from duck.errors import FatalError

def main(argv):
    try:
        return Frontend(Backend).run()
    except FatalError:
        sys.exit(111)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
