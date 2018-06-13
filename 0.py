#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : 0.py
# Author            : coldplay <coldplay_gz@sina.cn>
# Date              : 13.06.2018 14:30:1528871414
# Last Modified Date: 13.06.2018 14:30:1528871414
# Last Modified By  : coldplay <coldplay_gz@sina.cn>
# -*- coding: utf-8 -*-
# File              : 0.py
# Author            : coldplay <coldplay_gz@sina.cn>
# Date              : 13.06.2018 14:29:1528871353
# Last Modified Date: 13.06.2018 14:29:1528871362
# Last Modified By  : coldplay <coldplay_gz@sina.cn>

from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
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
from utils.link import Link
from click_mode import ClickMode
from input_mode import InputMode
myprint = Color()
workpath = os.getcwd()

isdebug = False

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
    def __init__(self,logger,db,task_id,q,pids):
        super(ChinaUSearch, self).__init__(logger,db,task_id,q,pids)
        myprint.print_green_text(u"引擎:配置浏览器")
        self.profile_type = 1
        self.webdriver_config()
        self.logger = logger
        self.detialpage_div = None
        self.detialpage_url = []
        self.script = Script(self.browser,logger)   
        myprint.print_green_text(u"引擎:初始化浏览器成功")


    #虚拟机上浏览器的配置
    def webdriver_config(self):
        try:
            # mapping = {
                # "1" : ".pc",
                # "2" : ".wap"
            # }
            # sql = "select path from profiles where id = {profile_id}".format(profile_id=self.profile_id)
            # res = self.db.select_sql(sql, 'DictCursor')
            # if res is None or len(res) == 0:
                # self.logger.error("can't get information profile_path")
            # self.origin_profile = res[0]['path']
            # print self.origin_profile
            l = Link("/home/pi/.mozilla/firefox/q9wwlcky.default",
                    'jid1-AVgCeF1zoVzMjA@jetpack.xpi',
                    'cookies.sqlite')
            l.link_ext("extensions", self.profile_id)
            l.link_cookie("", self.profile_id)
            l.link_prefs("", self.profile_id)

            if isdebug == True:
                self.browser = webdriver.Firefox()
            else:
                #self.browser = webdriver.Firefox()
                fp = webdriver.FirefoxProfile("/home/pi/.mozilla/firefox/q9wwlcky.default")
                # #fp.set_preference('permissions.default.image', 2)
                self.browser = webdriver.Firefox(fp)
            # self.browser = webdriver.Chrome()
            self.click_mode=ClickMode(self.browser, self.server_id,self.db,isdebug,"d:\\selenium\\000.jb")
            self.input_mode=InputMode(self.browser)
        except Exception,e:
            print (u"配置浏览器失败,{0}".format(e))
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
            self.update_db_log()
            self.success_add()
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
            self.update_db_log()
            self.success_add()
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
            self.update_db_log()
            self.success_add()
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

    # sooxie搜索
    def sooxie_search(self, keyword, num):
        try:
            self.browser.get('''https://www.sooxie.com/''')
            sleep(1)
            self.update_db_log()
            self.success_add()
            sleep(5)
            if self.random_click_on_page(num):
                for i in range(random.randint(1,3)):
                    self.go_to_next_page(num)
                    self.random_click_on_page(num)
                return True
            else:
                return False
            return True
        except Exception, e:
            self.logger.error(e)
            return False

    def typd3(self, select1, select):  # 0循环判断目标(绑句柄)
        ab = True  # 循环次数到后是否失败
        for n in range(select1):  # 循环找的次数
            ret = self.zdyx(select)  # 找到标签
            if ret != 0:
                self.switch_to_new_windows()  # 绑定窗口
                sleep(2)
                ab = False
                continue
            else:
                ab = True
                break  # 找到，成功，跳出循环

    def sogotowz(self, select, select1, select2):  # 0模拟键盘操作后回车（输入内容）
        print('sogotowz---')
        try:
            # self.switch_to_new_windows()
            ele = WebDriverWait(self.browser, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, select)))
            ele.send_keys(Keys.CONTROL + 'a')
            ele.send_keys(select1)
            print('found {0}'.format(select))
            ele = WebDriverWait(self.browser, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, select2)))
            ele.send_keys(Keys.ENTER)
            print('found {0}'.format(select2))
            # self.browser.find_element_by_xpath(select).send_keys(select1)
            # self.browser.find_element_by_xpath(select2).send_keys(Keys.ENTER)
            return 0
        except Exception, e:
            print(str(e.message))
            print("Can't Found The h3 tags")
            sleep(10)
            return -1

    def Process_360SearchPage(self):  # 0滚轮到底(2分钟)
        print(u"360搜索页中的动作")
        # 一分钟内的事情：从上到下移动滚动条
        # 这里的方法是，把页面高度分为60段，每秒从每段距离里随机移动距离，直到这段距离完成后进行下一段的移动，可变
        try:
            # self.switch_to_new_windows()
            pageheight = self.browser.execute_script('''return document.body.scrollHeight''')
            moveh = 0
            nowh = 0
            for j in range(60):
                endtime = 1000  # 即10秒
                moveh = (pageheight / 60) * (j + 1)  # 应该移动到的距离
                ymove = moveh - nowh  # 可移动的距离
                while endtime > 0:
                    i = random.randint(1, endtime)  # 0.1到10秒里随机
                    if i < 10:
                        i = 10
                    ranmove = random.randint(0, ymove)  # 随机移动距离，但不超过可移动距离
                    nowh = nowh + ranmove
                    ymove = ymove - ranmove
                    if ymove <= 0:
                        ymove = 0
                    js = "var q=document.documentElement.scrollTop={ran}".format(ran=nowh)
                    self.browser.execute_script(js)
                    s = i * 0.001
                    sleep(s)
                    endtime = endtime - i
            print(u"360搜索页中的动作完成")
            return 0
        except Exception, e:
            print(u'360搜索页操作错误:' + str(e))
            return -1

    def zdyx(self, select):
        try:
            self.switch_to_new_windows()
            print(u'zdyx查找元素:{0}'.format(select))
            ele = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, select)))
            # ele.send_keys(Keys.ENTER)
            # self.browser.find_element_by_xpath(select)#.send_keys(Keys.ENTER)
            sleep(1)
            print(u'找到元素')
            return 0
        except Exception, e:
            print(u"找不到目标:{0}".format(select))
            return -1

    def baiduSearchsod(self, select, target, lj1, lj2, x1, y1):  # 0鼠标移动点击(查找两个元素)
        try:
            titles = WebDriverWait(self.browser, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, select)))
        except Exception, e:
            print(u"错误")
            return -1
        for t in titles:
            if t.text.find(target) != -1:
                if lj1 == "":
                    self.process_dj(t)  # 直接点击(无操作鼠标)
                if lj1 != "":
                    self.process_ljd(t)  # 找到链接(针对58显示)
                    self.go_to_next_page12(target, lj1, lj2, x1, y1)  # 移动点击(操作鼠标)
                    self.switch_to_new_windows()  # 绑定窗口
                return 0

    def GetDetailUrl(self, iframeselect, select, div):  # 0取得详细页URL
        print(u'取得详细页URL，存入数组')
        print(u'取得详细面URL:' + select)
        try:
            # self.switch_to_new_windows()
            if iframeselect != "":
                ifr = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, iframeselect)))
                self.browser.switch_to_frame(ifr)
            print(self.browser.title)
            news_as = WebDriverWait(self.browser, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, select)))
            self.detialpage_url = []
            print(str(len(news_as)))
            for a in news_as:
                url = a.get_attribute("href")
                self.detialpage_url.append(url)

            if div != "":
                self.detialpage_div = WebDriverWait(self.browser, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, div)))
            self.browser.switch_to.default_content()
            print(u'取得详细面URL成功')
            return 0
        except Exception, e:
            print(u'取得详细页URL错误:' + str(e))
            return -1

    def OpenDetialPage(self):  # 0随机打开一条详细页
        print(u"随机打开一条详细页")
        urlcount = len(self.detialpage_url)
        print(urlcount)
        if urlcount <= 0:
            print(u'详细页URL数量为0')
            return -1

        try:
            openurl = random.choice(self.detialpage_url)
            print(openurl)
            try:
                with self.wait_for_new_window(self.browser):
                    self.browser.execute_script("window.open('{0}')".format(openurl))

            except Exception, e:
                openurl = random.choice(self.detialpage_div)  # 有URL就点URL，没有就点DIV
                self.click_mode.signal_pausing()
                openurl.click()
                print('click')
            print(u"随机打开一条详细页成功")
            sleep(5)
            return 0
        except Exception, e:
            strerr = str(e)
            if strerr.find('Timed out waiting for page load') != -1:
                print(u"随机打开一条详细页成功")
                return 0
            print(u'打开详细页错误:' + str(e))
            return -1

    def switch_to_new_windows(self):
        print(u"引擎:切换标签")
        sleep(6)
        windows = self.browser.window_handles
        # self.browser.switch_to_window(windows[-1])
        index = len(windows) - 1
        while index < len(windows):
            self.browser.switch_to.window(windows[index])
            sleep(1)
            try:
                url = self.browser.current_url
            except Exception, e:
                index -= 1
                continue
            if url != "":
                break;
            index -= 1
        sleep(3)

    @contextmanager
    def wait_for_new_window(self, driver, timeout=20):
        handles_before = driver.window_handles
        print "len:", len(handles_before)
        yield
        WebDriverWait(driver, timeout).until(
            lambda driver: len(handles_before) != len(driver.window_handles))

    def process_ljd(self, title):  # 针对58搜索链接显示处理
        print(u'E')
        #title.send_keys(Keys.END)
        sleep(2)
        title.send_keys(Keys.CONTROL+'c')
        print(u'找到链接')
        sleep(3)
#----------------------------------------------------------------
    def GoToIndexPage(self,url):    #0新键标签页输入网址
        print(u"打开首页")
        try:
            print (url)
            self.browser.execute_script("window.open('{0}')".format(url))
            self.switch_to_new_windows()
            print(u"打开网页成功"+url)
            return 0
        except Exception, e:
            strerr = str(e)
            if strerr.find('Timed out waiting for page load') != -1:
                print(u"打开网页成功" + url)
                return 0
            print(u'打开首页错误:'+str(e))
            sleep(1)
            return -1

            # 1搜索内容u"com"  2目标标签"a"(填写""鼠标不移动直接打开)  3点击 pyautogui(填写""不点击)  4和5相对移动X轴Y轴(鼠标移动到目标后,填写""不移动)

    def go_to_next_page12(self, target, lj1, lj2, x1, y1):  # 0移动鼠标点击    查找当前显示效果文字
        try:
            titles = WebDriverWait(self.browser, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, lj1)))  # 查找当前显示效果文字
            for t in titles:
                if t.text.find(target) != -1:
                    print("1")
                    left = self.browser.execute_script(
                        '''function getElementViewLeft(element){var actualLeft=element.offsetLeft;var current=element.offsetParent;while(current!==null){actualLeft+=current.offsetLeft;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollLeft=document.body.scrollLeft}else{var elementScrollLeft=document.documentElement.scrollLeft}return actualLeft-elementScrollLeft};return getElementViewLeft(arguments[0])''',
                        t)
                    top = self.browser.execute_script(
                        '''function getElementViewTop(element){var actualTop=element.offsetTop;var current=element.offsetParent;while(current!==null){actualTop+=current.offsetTop;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollTop=document.body.scrollTop}else{var elementScrollTop=document.documentElement.scrollTop}return actualTop-elementScrollTop};return getElementViewTop(arguments[0])''',
                        t)
                    top += 95 + 5
                    left += 20 + 20
                    print(u"移动")
                    pyautogui.moveTo(left, top, duration=3)  # 移动速度duration (多少秒)
                    sleep(1)
                    if x1 != "":
                        pyautogui.moveRel(x1, y1, duration=2)  # 鼠标当前相对移动距离
                    sleep(1)
                    if lj2 != "":  # run中第三个位填写pyautogui就会点击填写""就不会点击
                        lj2.click()
                        print(u"点击")
                        sleep(3)
                    return 0
        except Exception, e:
            print(str(e))
            print(u"移动错误")
            return -1

    def DoPC(self,keyword):
        ch = random.randint(1, 100)
        if ch > 100:  # 大于多少执行
            res = self.GoToIndexPage("http://www.baidu.com/")  # 打开网址
            if res != 0:
                return False
            sleep(5)
            self.typd3(3, "input#kw")
            ret = self.sogotowz("input#kw", u"58同城", "input#su")  # 搜索百度
            if ret != 0:  # 1输入框2输入内容3搜索键
                return False
            sleep(5)
            ch = random.randint(1, 100)
            if ch > 100:  # 大于50执行
                ret = self.Process_360SearchPage()  # 滚轮
                if ret != 0:
                    return False
            ret = self.baiduSearchso1(6, "div.f13", u"www.58.com", "a", pyautogui, "", "", "a.n", u"下一页>")  # 鼠标移动点击网址
            if ret != True:  # 1多少页  2链接属性（标题是h3 普通链接div.f13） 3目标链接标签名 4链接"a"标签代表点击打开（填写""代表直接打开链接）  5填写pyautogui就会点击，填写""就鼠标移动过去但不会点击
                print(u"找不到")  # 最后两个为鼠标当前位置的X和Y轴
                return False

            sleep(5)
            self.typd3(3, "div.bar_left,div#header-home-title,a.entrance")

        else:
            res = self.GoToIndexPage("http://www.58.com/")  # 打开网址
            if res != 0:
                return False
            sleep(5)
            self.typd3(3, "div.bar_left,div#header-home-title,a.entrance")

        print(u"判断")
        ret = self.zdyx("div#header-home-title,a.entrance")
        if ret == 0:
            print(u"进入")
            ret = self.baiduSearchsod("div#header-home-title,a.entrance", "", "div#header-home-title,a.entrance",
                                      pyautogui, "", "")  # 鼠标移动点击网址
            if ret != 0:  # 1多少页  2链接属性（标题是h3 普通链接div.f13） 3目标链接标签名 4链接"a"标签代表点击打开（填写""代表直接打开链接）  5填写pyautogui就会点击，填写""就鼠标移动过去但不会点击
                print(u"找不到")  # 最后两个为鼠标当前位置的X和Y轴
                return False
            self.typd3(3, "div.bar_left")

        ret = self.GetDetailUrl("",
                                "div.fl.cbp1.cbhg>div.board:nth-child(1)>span>a,div.fl.cbp1.cbhg>div.board:nth-child(1)>a,div.fl.cbp2.cbhg>div.board:nth-child(1)>span>em>a,div.fl.cbp2.cbhg>div.board:nth-child(1)>span>a",
                                "")  # 取得详细页URL 比如：第一个填的是可以点击的标签,第二个是div,如果第一个点不了就点击第二个
        if ret != 0:  # 收集详细页
            return -1
        ret = self.OpenDetialPage()  # 随机打开一条详细页
        if ret != 0:
            return -1

        self.typd3(3, "div.nav.float_l,div.nav,div.nav-top-bar.c_888.f12,div.site-nav.fl,div.crumbs_navigation")

        ret = self.GetDetailUrl("",
                                "div.tdiv>a,a.title.t,div.list-info.warehouse>h2>a,table.tbimg.kcc_tsys>tbody>tr>td:nth-child(2)>a.t,div.infocon>table>tbody>tr.zzinfo>td.t>a,div.list-info>h2>a,div.item-mod>div>a:nth-child(1),div.des>h2>a:nth-child(1)",
                                "")  # 取得详细页URL 比如：第一个填的是可以点击的标签,第二个是div,如果第一个点不了就点击第二个
        if ret != 0:  # 收集详细页
            return -1
        ret = self.OpenDetialPage()  # 随机打开一条详细页
        if ret != 0:
            return -1

        sleep(5)
        print('quit')
        sleep(5)
        return 0

    def DoWAP(self,keyword):
        ret = self.GoTo58()
        if ret != 0:
            return -1
        ret = self.FindTitlePhone(keyword)
        if ret != 0:
            # 未能找到目标
            if ret == -5:#搜索完成但没找到
                #self.ReportNotFound()
                print(u"搜索完成但没找到对应关键字")
                return 0
            return -1 #搜索一半出错
        else:
            #self.Report()
            print(u"搜索完成")
            return 0

    def search_58(self,keyword,num):
        self.update_db_log()
        self.success_add()
        if self.terminal_type == 2:#wap
            res = self.DoWAP(keyword)
        elif self.terminal_type == 1:#pc
            res = self.DoPC(keyword)

        if res == 0:
            return True
        else:
            return False


#----------------------------------------------------------
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
        self.click_mode.signal_pausing()
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
        try:
            a_tag = title.find_element_by_css_selector("a:first-child")
        except Exception,e:
            a_tag = title
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
        self.click_mode.signal_pausing()
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
            elif num == 6:
                elems = self.script.find_element_css_list("div.pro")
                titleflag = "span"
            sleep(5)
            if elems != None:
                for ele in elems:
                    title = self.script.find_elem("tag", titleflag, ele)
                    ahref = self.script.find_elem("tag", "a", ele)
                    print ahref
                    if title == None or ahref == None:
                        continue
                    if ele.is_displayed():
                        newsres.append(ele)
                if len(newsres) >= 1:
                    ranres = random.sample(newsres, 1)
                    for ran in ranres:
                        sleep(3)
                        if num == 4 or num==6:
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
        sleep(3)
        if sys.platform != 'win32':
            self.browser.quit()
            return
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
    myprint.print_green_text(u"程序 0.py 2018/05/12() 初始化中")
    global taskid
    parser = optparse.OptionParser()
    parser.add_option("-t", "--task_id", dest="taskid")
    (options, args) = parser.parse_args()
    taskid = options.taskid
    if isdebug == True:
        taskid = 3968251#3896222
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


def get_ip():  # 取得当前IP地址
    url = "http://packs.6a.com/site/clientip"
    request = urllib2.urlopen(url)
    response = request.read()
    return re.search('\d+\.\d+\.\d+\.\d+', response).group(0)


def write_ip_to_vm_cur_task(db,taskid):  # 写入到vm_cur_task里
    #ip = get_ip()
    ip = '127.0.0.1'
    sql = "update vm_cur_task set ip='{0}' where id={1}".format(ip,taskid)
    ret = db.execute_sql(sql)
    if ret < 0:
        print(u"写入运行时IP出错")
        return -1
    return 0

def run():
    q = Queue.Queue()
    myprint.print_green_text(u"获取任务中")
    db,logger =  configdb("DB_vm")

    write_ip_to_vm_cur_task(db,taskid) #写入运行时IP到vm_cur_task表

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
        print(u"user_type:{0}".format(usertype))
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
        elif usertype == 6:
            flag = engine.sooxie_search(keyword, usertype)
        elif usertype == 7:
            flag = engine.search_58(keyword,usertype)

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
    global isdebug
    s = len(sys.argv)
    if s <= 1:
        isdebug = True
    else:
        isdebug = False

    init() #配置任务
    try:
        run()  #执行任务
    except Exception,e:
        myprint.print_red_text(u"引擎:执行任务失败{0}".format(e))


if __name__ == "__main__":
    main()



























