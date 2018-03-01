#!/usr/bin/env python    
#encoding: utf-8  

import pyautogui
import random
import os

class ClickMode(object):
    def __init__(self, browser, jb_path = None):
        self.browser = browser
        self.jb_path = jb_path
        
    def write_position(self,x, y):
        operlist = []
        steplist = []
        curx = x
        cury = y
        i = 0
        while i<20:
            randx = random.randint(1,2)
            posx = curx- randx
            randy = random.randint(1,2)
            posy = cury+ randy
            print posx,posy
            movestr = "移动鼠标:{0},{1}\n".format(posx, posy)
            operlist.append(movestr)
            curx = posx
            cury = posy
            i += 1
      
        operlist.reverse()
        movestr = "移动鼠标:{0},{1}\n".format(x, y)
        waitstr = "延迟:{0}\n".format(random.randint(100, 600))
        movesetp = random.randint(10,30)
        steplist.append(movestr)
        j = 0
        while j < movesetp:
            rannum = random.randint(1,2)
            movestr = "移动鼠标:{0},{1}\n".format(x+rannum, y)
            steplist.append(movestr)
            j = j + rannum
            x = x+rannum
        operlist.extend(steplist)
        finallist = ['延迟:100\n','鼠标按下\n',waitstr,'鼠标弹起']
        operlist.extend(finallist)
        with open(self.jb_path, 'w') as f:
            f.writelines(operlist)

    def click_by_zhixing(self, top, left):
        step = random.randint(20, 150)
        top += 110
        left += step
        self.write_position(left,top)
        os.system(self.jb_path)
    
    def click_by_autogui(self, top, left):
        ran = random.randint(1, 7)
        pyautogui.moveTo(left, top, duration=ran)
        pyautogui.click()
    
    def click_by_sciprt(self, tag):
        self.browser.execute_script("arguments[0].click()", tag)

    def click(self, top, left, tag, mode=1):
        '''
        mode 1:zhixing
        mode 2:autogui
    '''
        if mode == 1:
            print "click by zhixing"
            self.click_by_zhixing(top, left)
        elif mode == 2:
            self.click_by_autogui(top, left) 
        else:
            print "click by script"
            self.click_by_sciprt(tag)

