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
from click_mode import ClickMode
from input_mode import InputMode
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
    def __init__(self,logger,db,task_id,q,pids,profile_type=1):
        super(ChinaUSearch, self).__init__(logger,db,task_id,q,pids)
        myprint.print_green_text(u"引擎:配置浏览器")
        self.profile_type = profile_type
        self.webdriver_config()
        self.logger = logger
        self.script = Script(self.browser,logger)   
        myprint.print_green_text(u"引擎:初始化浏览器成功")


    #虚拟机上浏览器的配置
    def webdriver_config(self):
        try:
            mapping = {
                "1" : ".pc",
                "2" : ".wap"
            }
            sql = "select path from profiles where id = {profile_id}".format(profile_id=self.profile_id)
            res = self.db.select_sql(sql, 'DictCursor')
            if res is None or len(res) == 0:
                self.logger.error("can't get information profile_path")
            self.origin_profile = res[0]['path']
            print self.origin_profile
            fp = webdriver.FirefoxProfile(self.origin_profile)
            #fp.set_preference('permissions.default.image', 2)
            self.browser = webdriver.Firefox(fp)
            #self.browser = webdriver.Chrome()
            self.click_mode=ClickMode(self.browser, "d:\\selenium\\000.jb")
            self.input_mode=InputMode(self.browser)
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
            print "配置浏览器失败,{0}".format(e)
            self.set_task_status(9)  # 任务提供的profileid 的path为NULL
            self.q.put(0)
            sys.exit(1)


    #搜狗搜索
    def sogou_search(self,keyword,num):
        try:
            self.browser.get('''https://www.sogou.com''')
            sleep(1)
            self.update_db_log()
            self.success_add()
            input_block = self.browser.find_element_by_xpath('''//*[@id="query"]''')
            self.input_mode.input(input_block, keyword, "query")
            input_block.send_keys(Keys.ENTER)
            sleep(2)
            if self.random_click_on_page(num):
                for i in range(random.randint(1,3)):
                    self.go_to_next_page(num)
                    self.random_click_on_page(num)
                return True
            else:
                return False
        except Exception,e:
            self.logger.error(e)
            return False

    # 360搜索
    def so_search(self,keyword,num):
        try:
            self.browser.get('''https://www.so.com''')
            sleep(1)
            self.update_db_log()
            self.success_add()
            input_block = self.script.find_elem("id","input")
            self.input_mode.input(input_block, keyword, "input")
            input_block.send_keys(Keys.ENTER)
            sleep(2)
            if self.random_click_on_page(num):
                for i in range(random.randint(1,3)):
                    self.go_to_next_page(num)
                    self.random_click_on_page(num)
                return True
            else:
                return False
        except Exception,e:
            self.logger.error(e)
            return False

    # 百度搜索
    def baidu_search(self,keyword,num):
        try:
            self.browser.get('''http://www.baidu.com''')
            sleep(1)
            self.update_db_log()
            self.success_add()
            input_block = self.browser.find_element_by_xpath('''//*[@id="kw"]''')
            self.input_mode.input(input_block, keyword, "kw")
            input_block.send_keys(Keys.ENTER)
            sleep(2)
            if self.random_click_on_page(num):
                for i in range(random.randint(1,3)):
                    self.go_to_next_page(num)
                    self.random_click_on_page(num)
                return True
            else:
                return False
        except Exception,e:
            self.logger.error(e)
            return False

    #中国搜索
    def china_search(self,keyword,num):
        try:
            self.browser.get('''http://www.chinaso.com/''')
            sleep(1)
            input_block = self.browser.find_element_by_xpath('''//*[@id="q"]''')
            self.input_mode.input(input_block, keyword, "q")
            input_block.send_keys(Keys.ENTER)
            if self.random_click_on_page(num):
                for i in range(random.randint(1,3)):
                    self.go_to_next_page(num)
                    self.random_click_on_page(num)
                return True
            else:
                return False
        except Exception,e:
            self.logger.error(e)
            return False

    # Bing搜索
    def bing_search(self, keyword, num):
        try:
            self.browser.get('''https://www.bing.com/''')
            sleep(1)
            input_block = self.browser.find_element_by_xpath('''//*[@id="sb_form_q"]''')
            self.input_mode.input(input_block, keyword, "sb_form_q")
            input_block.send_keys(Keys.ENTER)
            if self.random_click_on_page(num):
                for i in range(random.randint(1, 3)):
                    self.go_to_next_page(num)
                    self.random_click_on_page(num)
                return True
            else:
                return False
        except Exception, e:
            self.logger.error(e)
            return False

    # yahoo搜索
    def yahoo_search(self, keyword, num):
        try:
            self.browser.get('''https://www.yahoo.com/''')
            sleep(1)
            input_block = self.browser.find_element_by_xpath('''//*[@id="uh-search-box"]''')
            self.input_mode.input(input_block, keyword, "uh-search-box")
            input_block.send_keys(Keys.ENTER)
            if self.random_click_on_page(num):
                for i in range(random.randint(1, 3)):
                    self.go_to_next_page(num)
                    self.random_click_on_page(num)
                return True
            else:
                return False
        except Exception, e:
            self.logger.error(e)
            return False

    # gcn.6a.com搜索
    def gcn_search(self):
        try:
            self.browser.get('''http://www.baidu.com/''')
            sleep(5)
            self.browser.get('''http://gcn.6a.com/''')
            sleep(10)
            return True
        except Exception, e:
            self.logger.error(e)
            return False



    def go_to_next_page(self,num):
        try:
            sleep(3)
            if num == 0:
                pagebtns = self.script.find_element_css_list("a.n")
                for a in pagebtns:
                    if a.text == u"下一页>":
                        anext = a
            elif num == 1:
                anext = self.script.find_elem("id","snext")
            elif num == 2:
                anext = self.script.find_elem("id", "sogou_next")
            elif num == 3:
                pagebtns = self.script.find_element_css_list("a.pageBtn")
                for a in pagebtns:
                    if a.text == u"下一页>":
                        anext = a
            elif num == 4:
                anext = self.script.find_elem("css", "a.sb_pagN")
            elif num == 5:
                anext = self.script.find_elem("css", "a.next")
            if anext != None:
                if num == 5:
                    self.move_to_next_btn(anext,95)
                else:
                    self.move_to_next_btn(anext)
                self.browser.execute_script("arguments[0].click()", anext);
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
        availHeight = self.browser.execute_script("return window.document.documentElement.clientHeight;")
        top = self.browser.execute_script(
            '''function getElementViewTop(element){var actualTop=element.offsetTop;var current=element.offsetParent;while(current!==null){actualTop+=current.offsetTop;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollTop=document.body.scrollTop}else{var elementScrollTop=document.documentElement.scrollTop}return actualTop-elementScrollTop};return getElementViewTop(arguments[0])''',
            title)
        if top > availHeight:
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
        left += 30
        ran = random.randint(3, 7)
        pyautogui.moveTo(left, top, duration=ran)
        pyautogui.keyDown('ctrl')
        pyautogui.click()
        pyautogui.keyUp('ctrl')


    #在页面上随机点击
    def random_click_on_page(self,num):
        try:
            nowhandle = self.browser.current_window_handle
            newsres = []
            titleflag ="h3"
            if num == 0:
                elems = self.script.find_element_css_list("div.c-container")
            elif num == 1:
                elems = self.script.find_element_css_list("li.res-list")
            elif num == 2:
                elems = self.script.find_element_css_list("div.vrwrap,div.rb")
            elif num == 3:
                elems = self.script.find_element_css_list("li.reItem")
                titleflag = "h2"
            elif num == 4:
                elems = self.script.find_element_css_list("li.b_algo")
                titleflag = "h2"
            elif num == 5:
                elems = self.script.find_element_css_list("div.dd.algo.algo-sr")
            if elems != None:
                for ele in elems:
                    title = self.script.find_elem("tag", titleflag, ele)
                    ahref = self.script.find_elem("tag", "a", ele)
                    if title == None or ahref == None:
                        continue
                    if ele.is_displayed():
                        newsres.append(ele)
                if len(newsres) >= 1:
                    ranres = random.sample(newsres, 1)
                    for ran in ranres:
                        sleep(3)
                        if num == 4:
                            self.process_block(ran,120)
                        else:
                            self.process_block(ran)
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
        if self.copy_cookie == 1:
            if os.system("XCOPY /E /Y /C " + profiletmp + "\*.* " + self.origin_profile):
                print "files should be copied :/"
        self.browser.quit()
        sleep(5)
        shutil.rmtree(profiletmp, True)




def init():
    myprint.print_green_text(u"程序初始化中")
    global taskid
    parser = optparse.OptionParser()
    parser.add_option("-t", "--task_id", dest="taskid")
    (options, args) = parser.parse_args()
    taskid = options.taskid
    myprint.print_green_text(u"程序初始化完成, 获取到任务id:{id}".format(id = options.taskid))


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

    # for i in range(1, 4):
    #     sql = """select keyword from keyword_lib order by rand() limit 1""".format(taskid)
    #     ret = db.select_sql(sql, 'DictCursor')
    #     if ret:
    #         keyword = ret[0]['keyword'].decode("utf8")
    #         engine = ChinaUSearch(logger, db, taskid, q)
    #         try:
    #             if i == 1:
    #                 flag = engine.baidu_search(keyword, i)
    #             elif i == 2:
    #                 flag = engine.so_search(keyword, i)
    #             elif i == 3:
    #                 flag = engine.sogou_search(keyword, i)
    #             if flag:
    #                 sleep(10)
    #                 myprint.print_green_text(u"引擎:子任务完成，准备更新数据库状态")
    #                 engine.task_finished()
    #                 myprint.print_green_text(u"引擎:成功更新数据库，准备退出")
    #             else:
    #                 myprint.print_red_text(u"引擎:搜索失败")
    #                 engine.task_failed()
    #             engine.quit()
    #             myprint.print_green_text(u"引擎:任务完成，正常退出")
    #             q.put(1)
    #         except Exception, e:
    #             engine.quit()
    #             myprint.print_red_text(u"引擎:搜索失败")
    #             logger.error(e)

    sql = """select keyword from keyword_lib order by rand() limit 1""".format(taskid)
    ret = db.select_sql(sql, 'DictCursor')
    if ret:
        keyword = ret[0]['keyword'].decode("utf8")
        pids = psutil.pids()
        # try:
        engine = ChinaUSearch(logger, db, taskid, q ,pids)
        usertype = engine.user_type
        if usertype == 0:
            flag = engine.baidu_search(keyword, usertype)
        elif usertype == 1:
            flag = engine.so_search(keyword, usertype)
        elif usertype == 2:
            flag = engine.sogou_search(keyword, usertype)
        elif usertype == 3:
            flag = engine.china_search(keyword, usertype)
        elif usertype == 4:
            flag = engine.bing_search(keyword, usertype)
        elif usertype == 5:
            flag = engine.yahoo_search(keyword, usertype)
        if flag:
            sleep(10)
            myprint.print_green_text(u"引擎:子任务完成，准备更新数据库状态")
            engine.task_finished()
            myprint.print_green_text(u"引擎:成功更新数据库，准备退出")
        else:
            myprint.print_red_text(u"引擎:搜索失败")
            engine.task_failed()
            return
        myprint.print_green_text(u"引擎:进入待机:%d s"%(engine.standby_time*60))
        sleep(engine.standby_time * 60)
        myprint.print_green_text(u"引擎:待机完成")
        engine.task_wait_finished()
        engine.quit()
        sleep(10)
        myprint.print_green_text(u"引擎:任务完成，正常退出")
        q.put(1)
        # except Exception, e:
        #     logger.error(u"搜索异常，引擎崩溃! {0}".format(e))
        #     myprint.print_red_text(u"引擎:搜索引擎崩溃")
        #     engine.closebroswer()


def main():
    init() #配置任务
    try:
        run()  #执行任务
    except Exception,e:
        myprint.print_red_text(u"引擎:执行任务失败{0}".format(e))


if __name__ == "__main__":
    main()



























