#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : screenshot.py
# Author            : coldplay <coldplay_gz@sina.cn>
# Date              : 06.04.2018 15:47:1523000842
# Last Modified Date: 27.06.2018 15:46:1530085610
# Last Modified By  : coldplay <coldplay_gz@sina.cn>
import os
import sys
if sys.platform == "win32":
    import win32gui
    from ctypes import *
    import ctypes
    from PIL import ImageGrab

    class RECT(ctypes.Structure):
        _fields_ = [('left', ctypes.c_int), ('top', ctypes.c_int),
                    ('right', ctypes.c_int), ('bottom', ctypes.c_int)]


class ScreenShot(object):
    def __init__(self, path, driver=None):
        self.path = path
        self.browser = driver

    def take(self):
        if sys.platform != 'win32':
            cmd = 'scrot -u -q 60 ' + self.path
            print cmd
            ret = os.system(cmd)
            if not ret:
                print "scrot succ"
            return
        # print 'go'
        rect = RECT()
        HWND = win32gui.GetForegroundWindow()
        # print HWND
        ctypes.windll.user32.GetWindowRect(HWND, ctypes.byref(rect))
        coordinate = (rect.left + 2, rect.top + 100, rect.right - 2,
                      rect.bottom - 20)
        pic = ImageGrab.grab(coordinate)
        # pic.show()
        pic.save(self.path, quality=50)


def main():
    # ss = ScreenShot("d:\\21.jpg")
    ss = ScreenShot("/tmp/21.jpg")
    ss.take()
    print "grabed"


if __name__ == "__main__":
    main()
