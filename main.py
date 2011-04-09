#!/usr/bin/python2
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from duck.frontend.wxwidgets import Frontend
from duck.backend.mpd import Backend

def main(argv):
    return Frontend(Backend).run()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
