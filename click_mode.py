#!/usr/bin/env python    
# -*- coding: utf-8 -*-
# File              : click_mode.py
# Author            : coldplay <coldplay_gz@sina.cn>
# Date              : 10.05.2018 10:45:1525920326
# Last Modified Date: 10.05.2018 15:45:1525938352
# Last Modified By  : coldplay <coldplay_gz@sina.cn>
#encoding: utf-8  

import pyautogui
import random
import os
import time

        
            

class ClickMode(object):
    def __init__(self, browser, server_id, db, is_debug_mode=0, jb_path = None):
        self.browser = browser
        self.jb_path = jb_path
        self.is_debug_mode = is_debug_mode
        self.server_id = server_id
        self.db = db

    def signal_pausing(self):
        self.signal_pause_waiting()
        self.signal_wakeup_waiting()

    def signal_pause_waiting(self):
        sql = '''select notify_pause from vpn_status where serverid=%d and
        notify_pause=1 '''%(self.server_id) 
        for i in range(0,6):
            res = self.db.select_sql(sql)
            if res is None or len(res)<=0:
                return 
            else:
                print ("===================signal pause waiting====================")
                time.sleep(5)
        
    def signal_wakeup_waiting(self):
        sql = '''select notify_pause from vpn_status where serverid=%d and
        notify_pause=1 and vpnstatus=1'''%(self.server_id) 
        for i in range(0,6):
            res = self.db.select_sql(sql)
            if res is None or len(res)<=0:
                return 
            else:
                print ("===================signal wakeup waiting====================")
                time.sleep(5)

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

    def click_by_zhixing(self, top, left, top_step = 110):
        step = random.randint(20, 150)
        top += 110
        left += step
        self.write_position(left,top)
        os.system("d:\\selenium\\test.bat")
    
    def click_by_autogui(self, top, left, top_step = 0, p_ctrl = False):
        top += top_step
        # left += 30
        ran = random.randint(1, 7)
        pyautogui.moveTo(left, top, duration=ran)
        if p_ctrl:
            pyautogui.keyDown('ctrl')
        pyautogui.click()
        if p_ctrl:
            pyautogui.keyUp('ctrl')
        # pyautogui.click()
    
    def click_by_script(self, tag):
        self.browser.execute_script("arguments[0].click()", tag)

    def click(self, top, left, tag, top_step,mode=1, p_ctrl=False):
        '''
        mode 1:zhixing
        mode 2:autogui
    '''

        if self.is_debug_mode:
            mode = 2

        if mode == 1:
            print "click by zhixing"
            self.click_by_zhixing(top, left)
        elif mode == 2:
            print "click by autogui"
            self.click_by_autogui(top, left, top_step, p_ctrl) 
        elif mode == 3:
            print "click by script"
            self.click_by_script(tag)
        else:
                print "no click"

