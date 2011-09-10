#!/usr/bin/env python
import sys
from os.path import dirname, abspath, split

def main(argv):
   sys.path.append(dirname(abspath(__file__)))
   from duck.frontend.wxwidgets import Frontend
   from duck.backend.mpd import Backend
   from duck.errors import FatalError
   return Frontend(Backend).run()

if __name__ == '__main__':
    try:
       sys.exit(main(sys.argv))
    except Exception, e:
       print 'duck: %s' % e
       try:
          errorcode = e.errcode
       except AttributeError:
          errorcode = 1
       sys.exit(errorcode)
