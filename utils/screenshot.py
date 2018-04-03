import win32gui
from ctypes import *
import ctypes
from PIL import ImageGrab


class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_int),
                ('top', ctypes.c_int),
                ('right', ctypes.c_int),
                ('bottom', ctypes.c_int)]

class ScreenShot(object):
    def __init__(self,path):
        self.path = path

    def take(self):
        print 'go'
        rect = RECT()
        HWND = win32gui.GetForegroundWindow()
        print HWND
        ctypes.windll.user32.GetWindowRect(HWND, ctypes.byref(rect))
        coordinate = (rect.left+2, rect.top+50, rect.right-2, rect.bottom-20)
        pic = ImageGrab.grab(coordinate)
        pic.show()
        pic.save(self.path,quality=50)
    
def main():
    ss = ScreenShot("d:\\21.jpg")
    ss.take()
    print "grabed"

if __name__ == "__main__":
    main()