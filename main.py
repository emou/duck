#!/usr/bin/python2
import sys
from os.path import dirname, abspath

sys.path.append(dirname(abspath(__file__)))
from duck.frontend.wxwidgets import Frontend
from duck.backend.mpd import Backend

def main(argv):
    return Frontend(Backend).run()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
