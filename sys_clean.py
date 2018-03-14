#!/usr/bin/env python    
#encoding: utf-8 

import sys
import psutil
from ColorPrint import Color
from time import sleep
import os
if sys.platform == 'win32':
    import win32gui
    import win32process
    import win32api
    import win32con
    import ctypes  

myprint = Color()


class SysClean(object):
    def __init__(self, logger, pids):
        self.logger = logger
        self.pids = pids

    def startup_check(self):
        '''检测是否出现错误窗口,存在则清除相关进程
        '''
        if sys.platform != 'win32':
            return
        myprint.print_green_text(u"引擎: 检查是否有遗留的浏览器进程")
        if not self.close_third_windows():
            self.checkclose()
            # self.checkclose()


    def closebroswer(self):
        if sys.platform != 'win32':
            return
        myprint.print_red_text(u"程序异常，准备杀死进程")
        currentpids = psutil.pids()
        for pid in currentpids:
            try:
                p = psutil.Process(pid)
                if p.name() == "geckodriver.exe" or p.name() == "firefox.exe":
                    print(u"关闭进程ID-%d,进程名-%s" % (pid, p.name()))
                    print self.closeprocess(pid), pid
                    sleep(1)
            except Exception,e:
                print(u"进程ID-%d,已被杀死" % (pid))
                continue



    def checkclose(self):
        myprint.print_red_text(u"检查程序残留进程")
        curpid = os.getpid()
        newpids = self.pids
        for pid in newpids:
            try:
                if pid != curpid:
                    p = psutil.Process(pid)
                    if p.name() == "geckodriver.exe" or p.name() == "firefox.exe" or p.name() == "python.exe":
                        print(u"关闭进程ID-%d,进程名-%s" % (pid, p.name()))
                        print self.closeprocess(pid), pid
                        sleep(1)
            except Exception,e:
                print(u"进程ID-%d,已被杀死" % (pid))
                continue


    def showpids(self,pids):
        myprint.print_green_text(u"显示当前进程：")
        currentpids = psutil.pids()
        newpids = list(set(currentpids).difference(set(pids)))
        for pid in newpids:
            p = psutil.Process(pid)
            if p.name() == "geckodriver.exe" or p.name() == "firefox.exe" or p.name() == "python.exe":
                print(u"进程ID-%d,进程名-%s,当前正在运行" % (pid, p.name()))


    def closeprocess(self,p):
        try:
            command = "taskkill /F /PID {0}".format(p)
            os.popen(command)
            return True
        except Exception, e:
            return False

    def isRealWindows(self,hwnd):
        # if IsWindow(hwnd) and IsWindowEnabled(hwnd) and IsWindowVisible(hwnd):
        if not win32gui.IsWindowVisible(hwnd):
            return False
        if win32gui.GetParent(hwnd) != 0:
            return False
        return True

    def getwin(self,title):
        def callback(hwnd, windows):
            if not self.isRealWindows(hwnd):
                return
            text = win32gui.GetWindowText(hwnd)
            pp = unicode(text, 'gbk')
            if pp.find(title) != -1:
                windows.append((hwnd))

        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows
    
    def close_third_windows(self):
        myprint.print_green_text(u"检测是否程序异常，关闭第三方窗口")
        titles = [u"geckodriver.exe",u"应用程序错误", u"崩溃报告器",u"python.exe",u"Firefox.exe"]
        flag = True
        try:
            for title in titles:
                hwnds = self.getwin(title)
                if len(hwnds) > 0:
                    for hwnd in hwnds:
                        rq = ctypes.windll.user32.IsHungAppWindow(hwnd)
                        if rq == 1:
                            print u"捕捉到windows第三方窗口：" + unicode(win32gui.GetWindowText(hwnd), 'gbk') + u",执行关闭"
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                            self.logger.error(u"关闭异常进程: " + unicode(win32gui.GetWindowText(hwnd), 'gbk') + u"成功")
                            sleep(2)
                            flag = False
                        elif title == u"崩溃报告器" or title == u"应用程序错误":
                            print u"捕捉到windows第三方窗口：" + unicode(win32gui.GetWindowText(hwnd), 'gbk') + u",执行关闭"
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                            self.logger.error(u"关闭异常进程: " + unicode(win32gui.GetWindowText(hwnd), 'gbk') + u"成功")
                            sleep(2)
                            flag = False
        except Exception,e:
            self.logger.error("关闭第三方窗口异常：{0}".format(e))
            return False
        if flag == True:
            myprint.print_green_text(u"引擎: 没有检测到异常")
        return flag
    
    def removePath(self,destinationPath):
        try:
            if os.path.exists(destinationPath):
                pathList = os.listdir(destinationPath)
                for path in pathList:
                    pathFull = os.path.join(destinationPath, path)
                    print pathFull
                    if os.path.isdir(pathFull):
                        self.removePath(pathFull)
                shutil.rmtree(destinationPath, True)
        except Exception,e:
            myprint.print_red_text(u"引擎: 删除临时文件夹报错")

    def deleteprofile(self):
        tempdir = r'C:\Users\Administrator\AppData\Local\Temp'
        self.removePath(tempdir)
