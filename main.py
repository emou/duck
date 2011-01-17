#!/usr/bin/python2

def main(argv):
    from duck.frontend.wxwidgets import Frontend
    from duck.backend.mpd import Backend
    return Frontend(Backend).run()

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main(sys.argv))
