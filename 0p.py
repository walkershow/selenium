#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from prototypecopy import prototype
from ColorPrint import Color
from script.script import Script
import importlib

from time import sleep
from dbutil import DBUtil
from pypinyin import pinyin, lazy_pinyin,Style
import wubi
import optparse
import ConfigParser
import logging
import logging.config
import requests
import urllib2
import urllib
import re
import os
import sys
import random
import math
import pyautogui
import multiprocessing
import Queue
import psutil
import shutil
import win32gui
import win32process
import win32api
import win32con
import cPickle as pickle

from click_mode import ClickMode
from input_mode import InputMode

isdebug = False #测试用

myprint = Color()
workpath = os.getcwd()

def drawSquare():
    rangeList = [
        (0, 360),
        (100, 200),
        (0, 100),
        (140, 200),
        (24, 320),
        (60, 120),
        (120, 180),
        (180, 240),
        (240, 300)
    ]
    randnum = random.randint(0, len(rangeList) - 1)
    rangex = rangeList[randnum][0]
    rangey = rangeList[randnum][1]
    width, height = pyautogui.size()
    roll = random.randint(height/2,2*height/3)
    r = 250
    s = random.randint(2, 5)
    o_x = width / s
    o_y = height / s
    pi = 3.1415926
    i = 0
    for angle in range(rangex, rangey, 5):
        X = o_x + r * math.sin(angle * pi / 180)
        Y = o_y + r * math.cos(angle * pi / 180)
        if i == 0:
            pyautogui.moveTo(X, Y, duration=1)
        else:
            pyautogui.moveTo(X, Y, duration=0.1)
        i = i + 1
    pyautogui.moveTo(190, 0)
    pyautogui.moveTo(190, roll, duration=s)



class ChinaUSearch(prototype):
    #user_type = 0
    def __init__(self,logger,db,task_id,q,pids,profile_type=2):
        super(ChinaUSearch, self).__init__(logger,db,task_id,q,pids)
        myprint.print_green_text(u"引擎:配置浏览器")
        self.profile_type = profile_type
        self.webdriver_config()
        self.logger = logger
        self.script = Script(self.browser,logger)
        myprint.print_green_text(u"引擎:初始化浏览器成功")

    #虚拟机上浏览器的配置
    def webdriver_config(self):
        print("web driver_config")
        try:
            mapping = {
                "1" : ".pc",
                "2" : ".wap"
            }
            sql = "select path from profiles where id = {profile_id}".format(profile_id=self.profile_id)
            res = self.db.select_sql(sql, 'DictCursor')
            if res is None or len(res) == 0:
                self.logger.error("can't get information profile_path")
            if isdebug == True:
                self.origin_profile = 'D:/profile/lhcjrry1.wapb1'#wapa59' #wapb1'#
            else:
                self.origin_profile = res[0]['path']
            print (self.origin_profile)
            fp = webdriver.FirefoxProfile(self.origin_profile)
            #fp.set_preference('permissions.default.image', 2)
            self.browser = webdriver.Firefox(fp)
            # self.browser = webdriver.Chrome()
            self.click_mode = ClickMode(self.browser, "d:\\selenium\\000.jb")
            self.input_mode = InputMode(self.browser)
            # self.profile_path = []
            # temp_folder = os.listdir("D:\\profile")
            # target = mapping[str(self.profile_type)]
            # for f in temp_folder:
            #     if f.find(target) != -1:
            #         self.profile_path.append(os.path.join("D:\\profile\\", f))
            # profile = random.sample(self.profile_path, 1)
            # print profile
            # fp = webdriver.FirefoxProfile(profile[0])
            # fp.set_preference('permissions.default.image', 2)
            # self.browser = webdriver.Firefox(fp)

        except Exception,e:
            print (u"配置浏览器失败,{0}".format(e))
            self.set_task_status(9)  # 任务提供的profileid 的path为NULL
            self.q.put(0)
            sys.exit(1)
    
    def input_pinyin(self,kw,keyword,kwid):
        for word in keyword:
            for w in lazy_pinyin(word)[0]:
                kw.send_keys(w)
                sleep(random.uniform(0.2, 1.5))
            js = ''' function replace_last_str(origin_str, target_str, replace_str){
                        var index = origin_str.lastIndexOf(target_str);
                        return origin_str.substr(0, index) + replace_str + origin_str.substr(index + target_str.length);
                    }
                    value = document.getElementById("{kwid}").value;
                    document.getElementById("{kwid}").value = replace_last_str(value, "{origin}", "{replace_str}")
                '''
            js = js.replace("{origin}", lazy_pinyin(word)[0]).replace("{replace_str}", word).replace("{kwid}",kwid)
            self.browser.execute_script(js)

    def input_wubi(self,kw,keyword,kwid):
        for word in keyword:
            for w in wubi.get(word,'cw'):
                kw.send_keys(w)
                sleep(random.uniform(0.2, 1.5))
            js = ''' function replace_last_str(origin_str, target_str, replace_str){
                        var index = origin_str.lastIndexOf(target_str);
                        return origin_str.substr(0, index) + replace_str + origin_str.substr(index + target_str.length);
                    }
                    value = document.getElementById("{kwid}").value;
                    document.getElementById("{kwid}").value = replace_last_str(value, "{origin}", "{replace_str}")
                '''
            js = js.replace("{origin}",  wubi.get(word, 'cw')).replace("{replace_str}", word).replace("{kwid}",kwid)
            self.browser.execute_script(js)


    def x_search(self,keyword,num,url,xpath,elementname):
        print(u'进入搜索')
        try:
            self.browser.get(url)
            sleep(1)
            self.browser.maximize_window()
            if(num == 0):
                try:#百度偶尔会弹提示框
                    tipsdlg = self.browser.find_element_by_css_selector("p.callappbox-wrap-chose-close")
                    print(u"百度提示框p.callappbox-wrap-chose-close")
                    tipsdlg.click()
                    #self.process_block(tipsdlg)
                except Exception,e:
                    pass
                try:
                    tipsdlg = self.browser.find_element_by_css_selector("button.callappbox-wrap-chose-close")
                    print(u"百度提示框button.callappbox-wrap-chose-close")
                    tipsdlg.click()
                    print(u"点击百度弹框")
                except Exception,e:
                    pass
            if num == 5:
                searchbutton = self.browser.find_element_by_id("uh-search-ph")
                searchbutton.click()
                sleep(1)
            self.update_db_log()
            self.success_add()
            input_block = self.browser.find_element_by_xpath(xpath)
            randnum = random.randint(0,1)
            if randnum == 0:
                self.input_pinyin(input_block,keyword,elementname)
            elif randnum == 1:
                self.input_wubi(input_block,keyword,elementname)
            input_block.send_keys(Keys.ENTER)
            sleep(2)
            searchurl = self.browser.current_url
            if self.random_click_on_page(num):
                for i in range(random.randint(1,3)):
                    nowurl = self.browser.current_url
                    if nowurl != searchurl:#偶尔会在搜索页窗口打开别的窗口，需要返回搜索页
                    #if self.user_type == 5:#yahoo 有点特殊，是在同一窗口打开的，需要返回到搜索页
                        sleep(5)
                        self.browser.back()
                        sleep(1)
                    self.go_to_next_page(num)
                    searchurl = self.browser.current_url
                    self.random_click_on_page(num)
                return True
            else:
                return False
        except Exception,e:
            self.logger.error(e)
            return False

    def scroll_to_next_page(self):#有些翻页不是点‘下一页’而是滚动滚动条进行翻页
        pageheight = self.browser.execute_script('''return document.body.scrollHeight''')
        js = "var q=document.documentElement.scrollTop={pos}".format(pos=pageheight + 600) #600可以调整，看情况定
        self.browser.execute_script(js)

    def go_to_next_page(self,num):
        try:
            sleep(3)
            if num == 0:#百度
                anext = self.script.find_elem("css","a.new-nextpage-only")
            elif num == 1:#360
                #anext = self.script.find_elem("id","new-nextpage-only")
                self.scroll_to_next_page() #向下滚动一定距离
            elif num == 2:#sogou
                #要滚两次才能滚到最下面
                js = "var q=document.documentElement.scrollTop=99999"
                self.browser.execute_script(js)
                js = "var q=document.documentElement.scrollTop=99999"
                self.browser.execute_script(js)
                anext = self.script.find_elem("id", "ajax_next_page")
            elif num == 3:#chinaso
                js = "var q=document.documentElement.scrollTop=99999"
                self.browser.execute_script(js)
                pagebtns = self.script.find_elem("a.loadmore-a")
            elif num == 4:#bing
                js = "var q=document.documentElement.scrollTop=99999"
                self.browser.execute_script(js)
                anext = self.script.find_elem("css", "div.sb_pagIconN")
            elif num == 5:#yahoo
                anext = self.script.find_elem("css", "a.next")
            if anext != None:
                
                self.move_to_next_btn(anext,130)
             #   self.browser.execute_script("arguments[0].click()", anext);
                sleep(3)
                return True
            else:
                return False
        except Exception, e:
            return False


    def move_to_next_btn(self,ele,step=110):
        availHeight = self.browser.execute_script("return window.document.documentElement.clientHeight;")
        top = self.browser.execute_script(
            '''function getElementViewTop(element){var actualTop=element.offsetTop;var current=element.offsetParent;while(current!==null){actualTop+=current.offsetTop;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollTop=document.body.scrollTop}else{var elementScrollTop=document.documentElement.scrollTop}return actualTop-elementScrollTop};return getElementViewTop(arguments[0])''',
            ele)
        if top > availHeight:
            ele.location_once_scrolled_into_view
        left = self.browser.execute_script(
            '''function getElementViewLeft(element){var actualLeft=element.offsetLeft;var current=element.offsetParent;while(current!==null){actualLeft+=current.offsetLeft;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollLeft=document.body.scrollLeft}else{var elementScrollLeft=document.documentElement.scrollLeft}return actualLeft-elementScrollLeft};return getElementViewLeft(arguments[0])''',
            ele)
        top = self.browser.execute_script(
            '''function getElementViewTop(element){var actualTop=element.offsetTop;var current=element.offsetParent;while(current!==null){actualTop+=current.offsetTop;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollTop=document.body.scrollTop}else{var elementScrollTop=document.documentElement.scrollTop}return actualTop-elementScrollTop};return getElementViewTop(arguments[0])''',
            ele)
        # 修正位置
        top += step
        left += 20
        pyautogui.moveTo(left, top, duration=1)
        pyautogui.click()
        sleep(3)


    def process_block(self, title,topstep=110):
        title.location_once_scrolled_into_view

        availHeight = self.browser.execute_script("return window.document.documentElement.clientHeight;")
        top = self.browser.execute_script(
            '''function getElementViewTop(element){var actualTop=element.offsetTop;var current=element.offsetParent;while(current!==null){actualTop+=current.offsetTop;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollTop=document.body.scrollTop}else{var elementScrollTop=document.documentElement.scrollTop}return actualTop-elementScrollTop};return getElementViewTop(arguments[0])''',
            title)
        if top >= availHeight-50 and availHeight > 100:
            self.browser.execute_script("return arguments[0].scrollIntoView();", title)
			
        self.browser.execute_script("window.scrollBy(0, -200);")
        drawSquare()
        a_tag = title.find_element_by_css_selector("a:first-child")
        print a_tag.get_attribute("href")
        left = self.browser.execute_script(
            '''function getElementViewLeft(element){var actualLeft=element.offsetLeft;var current=element.offsetParent;while(current!==null){actualLeft+=current.offsetLeft;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollLeft=document.body.scrollLeft}else{var elementScrollLeft=document.documentElement.scrollLeft}return actualLeft-elementScrollLeft};return getElementViewLeft(arguments[0])''',
            title)
        top = self.browser.execute_script(
            '''function getElementViewTop(element){var actualTop=element.offsetTop;var current=element.offsetParent;while(current!==null){actualTop+=current.offsetTop;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollTop=document.body.scrollTop}else{var elementScrollTop=document.documentElement.scrollTop}return actualTop-elementScrollTop};return getElementViewTop(arguments[0])''',
            title)
        # 修正位置
        top += topstep
        left += 50
        ran = random.randint(3, 7)
        pyautogui.moveTo(left, top, duration=ran)
        pyautogui.keyDown('ctrl')
        pyautogui.click()
        pyautogui.keyUp('ctrl')


    #在页面上随机点击
    def random_click_on_page(self,num):
        print(u"随机点击搜索内容")
        try:
            nowhandle = self.browser.current_window_handle
            newsres = []
            titleflag ="li"
            if num == 0:#百度
                titleflag = "a"
                elems = self.script.find_element_css_list("div.c-row")#div.hint-rcmd-item-container")#div.rn-container")
                print(u"找div.c-row")
            elif num == 1:#360
                elems = self.script.find_element_css_list("div.res-list")
                js = "if(document.documentElement&&document.documentElement.scrollTop){\
                    return document.documentElement.scrollTop; }else if(document.body){\
                    return document.body.scrollTop;}"
                scrolltop = self.browser.execute_script(js)
                for ele in elems:#过滤掉位置 大于 滚动条当前位置-300的
                    js = "function getElementTop(element){var actualTop = element.offsetTop;var current = element.offsetParent;\
                        while (current !== null){\
　　　　　　              actualTop += current.offsetTop;\
                          current = current.offsetParent;\
　　　　                }\
                        return actualTop;\
　　                  }"
                    top = self.browser.execute_script(js,ele)
                    if top < scrolltop-300:
                        elems.remove(ele)
                titleflag="a"
            elif num == 2:#sougou
                elems = self.script.find_element_css_list("div.vrResult")
                titleflag="div.vrResult>h3>a"
            elif num == 3:#chinaso
                elems = self.script.find_element_css_list("div.res-con>div")
                titleflag = "a"
            elif num == 4:#bing
                elems = self.script.find_element_css_list("li.b_algo")
                titleflag = "h2>a"
            elif num == 5:#yahoo
                elems = self.script.find_element_css_list("div.compTitle")#div.compTitle>h3>a
                titleflag = "h3>a"
            if elems != None:
                print()
                for ele in elems:
                    title = self.script.find_elem("css", titleflag, ele)
                   # ahref = self.script.find_elem("tag", "a", ele)
                    if title == None :#or ahref == None:
                       continue
                    #print (title.text)
                    if ele.is_displayed():
                        newsres.append(ele)
                if len(newsres) >= 1:
                    print('1')
                    ranres = random.sample(newsres,1)
                    print('2')
                    for ran in ranres:
                        print('3')
                        sleep(2)
                        if self.user_type == 0:#百度
                            print('4')
                            self.process_block(ran,130)
                        else:
                            self.process_block(ran,150)
                        sleep(5)
                        self.browser.switch_to.window(nowhandle)
            return True
        except Exception, e:
            print "搜索随机点击报错:{0}".format(e)
            self.logger.error(e)
            return False

    def quit(self):
        self.browser.get("about:support")
        profiletmp = self.browser.execute_script(
            '''let currProfD = Services.dirsvc.get("ProfD", Ci.nsIFile);
               let profileDir = currProfD.path;
               return profileDir
            '''
        )
        if os.system("XCOPY /E /Y /C " + profiletmp + "\cookies.sqlite " + self.origin_profile):
            print "files should be copied :/"
        shutil.rmtree(profiletmp, True)
        self.browser.quit()

def init():
    myprint.print_green_text(u"程序初始化中")
    global taskid
    parser = optparse.OptionParser()
    parser.add_option("-t", "--task_id", dest="taskid")
    (options, args) = parser.parse_args()
    taskid = options.taskid
    if isdebug == True:
        taskid = 3302859#2909392 #2782115
    myprint.print_green_text(u"程序初始化完成, 获取到任务id:{id}".format(id = taskid))


def configdb(dbname):
    logging.config.fileConfig("{0}/log_conf/task.log.conf".format(workpath))
    logger = logging.getLogger()
    cf = ConfigParser.ConfigParser()
    confpath="{0}/log_conf/db.conf".format(workpath)
    cf.read(confpath)
    db_host = cf.get(dbname,"db_host")
    db_name = cf.get(dbname,"db_name")
    db_user = cf.get(dbname,"db_user")
    db_pwd = cf.get(dbname,"db_pwd")
    db_charset = cf.get(dbname,"db_charset")
    db=DBUtil(logger,db_host,3306,db_name,db_user,db_pwd,db_charset)
    return db,logger

def run():
    q = Queue.Queue()
    myprint.print_green_text(u"获取任务中")
    db,logger =  configdb("DB_vm")

    sql = """select keyword from keyword_lib order by rand() limit 1""".format(taskid)
    ret = db.select_sql(sql, 'DictCursor')
    if ret:
        keyword = ret[0]['keyword'].decode("utf8")
        pids = psutil.pids() #进程号
        try:
   #         while 1:#一直循环，实验用
            engine = ChinaUSearch(logger, db, taskid, q ,pids)
            print(u"建立引擎对象成功")
            usertype = engine.user_type
            if isdebug == True:#实验
                usertype = random.randint(0, 5)
            if usertype == 0: #百度
                flag = engine.x_search(keyword, usertype,'''http://m.baidu.com''','''//*[@id="index-kw"]''',"index-kw")
            elif usertype == 1: #360
                flag = engine.x_search(keyword, usertype,'''https://www.so.com''','''//*[@id="q"]''',"q")
            elif usertype == 2: #搜狗
                flag = engine.x_search(keyword, usertype,'''https://www.sogou.com''','''//*[@id="keyword"]''',"keyword")
            elif usertype == 3: #china
                flag = engine.x_search(keyword, usertype,'''http://www.chinaso.com/''','''//*[@id="keys-head"]''',"keys-head")
            elif usertype == 4: #bing
                flag = engine.x_search(keyword, usertype,'''https://www.bing.com/''','''//*[@id="sb_form_q"]''',"sb_form_q")
            elif usertype == 5: #yahoo
                flag = engine.x_search(keyword, usertype,'''https://www.yahoo.com/''','''//*[@id="uh-search-box"]''',"uh-search-box")
            if flag:
                sleep(10)
                myprint.print_green_text(u"引擎:子任务完成，准备更新数据库状态")
                engine.task_finished()
                myprint.print_green_text(u"引擎:成功更新数据库，准备退出")
            else:
                myprint.print_red_text(u"引擎:搜索失败")
                engine.task_failed()
                engine.quit()
                return
            myprint.print_green_text(u"引擎:进入待机:%d s" % (engine.standby_time * 60))
            sleep(engine.standby_time * 60)
            myprint.print_green_text(u"引擎:待机完成")
            engine.task_wait_finished()
            engine.quit()
            sleep(10)
            myprint.print_green_text(u"引擎:任务完成，正常退出")
            q.put(1)
        except Exception, e:
            logger.error(u"搜索异常，引擎崩溃! {0}".format(e))
            myprint.print_red_text(u"引擎:搜索引擎崩溃")
            engine.closebroswer()


def main():
    init() #配置任务
    try:
        run()  #执行任务
    except Exception,e:
        myprint.print_red_text(u"引擎:执行任务失败{0}".format(e))


if __name__ == "__main__":
    main()



























