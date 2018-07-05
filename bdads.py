#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : bdadsy.py
# Author            : coldplay <coldplay_gz@sina.cn>
# Date              : 27.06.2018 11:28:1530070115
# Last Modified Date: 05.07.2018 15:13:1530774802
# Last Modified By  : coldplay <coldplay_gz@sina.cn>
# -*- coding: utf-8 -*-
# File              : bdads.py
# Author            : coldplay <coldplay_gz@sina.cn>
# Date              : 14.06.2018 10:42:1528944136
# Last Modified Date: 14.06.2018 10:42:1528944136
# Last Modified By  : coldplay <coldplay_gz@sina.cn>
import ConfigParser
import importlib
import logging
import logging.config
import math
import optparse
import os
import Queue
import random
import re
import shutil
import subprocess
import sys
import threading
import urllib
import urllib2
import traceback
from os.path import basename
from time import sleep, time
from urlparse import urlsplit

import dbutil
import psutil
import pyautogui
import requests
import wubi
from datetime import datetime, timedelta
from click_mode import ClickMode
from click_rate import ClickRate
from ColorPrint import Color
from input_mode import InputMode
from prototypecopy import prototype

from utils.picftp import PicFTP
from utils.link import Link
from utils.string_rect import GetTitleDimensions
if sys.platform == 'win32':
    from utils.screenshot import ScreenShot

from pypinyin import Style, lazy_pinyin, pinyin
from selenium import webdriver
from contextlib import contextmanager
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

myprint = Color()
workpath = os.getcwd()
profile_dir = None
home_dir = None
extension_name = None
cookie_name = None
g_step = 150


class ele_not_clickable(object):
    def __init__(self, count):
        self.count = count

    def is_ele_not_clickable(self, browser):
        try:

            selector = "#page > strong > span.pc"
            divs = WebDriverWait(browser, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                     selector)))
            print "*********", selector, "**********"
            print "find pagenum:", self.count
            for a in divs:
                print "not clicakble link text:", a.text
                if a.text == str(self.count):
                    print "ele is not clickable,new page"
                    return True
        except WebDriverException, e:
            print "exp clickable,old page"
            return False
        print "ele is clickable,old page"
        return False

    def __call__(self, driver):
        return self.is_ele_not_clickable(driver)


def drawSquare():
    rangeList = [(0, 360), (100, 200), (0, 100), (140, 200), (24, 320),
                 (60, 120), (120, 180), (180, 240), (240, 300)]

    randnum = random.randint(0, len(rangeList) - 1)
    rangex = rangeList[randnum][0]
    rangey = rangeList[randnum][1]
    width, height = pyautogui.size()
    roll = random.randint(height / 2, 2 * height / 3)
    r = random.randint(100, 300)
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
    xpos = random.randint(100, 200)
    xstep = random.randint(50, 100)
    ystep = random.randint(0, 50)
    pyautogui.moveTo(xpos, ystep)
    curx = xpos + xstep + 30
    cury = roll
    pyautogui.moveTo(curx, cury, duration=s)


class ChinaUSearch(prototype):
    def __init__(self, logger, db, task_id, q, pids, task, cm, is_ad,
                 is_debug_mode):
        myprint.print_green_text(u"引擎:初始化本体")
        super(ChinaUSearch, self).__init__(logger, db, task_id, q, pids, cm,
                                           is_ad, is_debug_mode)
        self.script_name = task["script_name"]
        self.title = task["title"]
        self.keyword = task["keyword"]
        self.url = task["url"]
        self.id = task["id"]
        self.rid = task["rid"]
        self.method = task["method"]
        self.random_event_status = task['random_event_status']
        self.total_page = task['total_page']
        self.start_search_page = task['start_search_page']
        self.terminal_type = task["terminal_type"]  # 终端
        self.profile_type = task["terminal_type"]
        self.onlysearch = task["onlysearch"]
        self.real_url = task["real_url"]
        self.origin_cookie = ""
        self.random_event_count = 0
        self.module = importlib.import_module(
            "script.{script_name}".format(script_name=self.script_name))
        self.loadstatus = True
        self.win_pos = 1
        self.last_ret = None
        myprint.print_green_text(u"引擎:初始化本体成功")
        myprint.print_green_text(u"引擎:初始化浏览器")
        self.webdriver_config()
        self.Wait = WebDriverWait(self.browser, 20)
        myprint.print_green_text(u"引擎:初始化浏览器成功")

    def webdriver_config(self):
        try:
            # mapping = {"1": ".pc", "2": ".wap"}
            # sql = "select path from profiles where id = {profile_id}".format(
            # profile_id=self.profile_id)
            # res = self.db.select_sql(sql, 'DictCursor')
            # if res is None or len(res) == 0:
            # self.logger.error("can't get information profile_path")
            # self.origin_profile = res[0]['path']

            # l = Link("/home/pi/.mozilla/firefox/q9wwlcky.default",
            # 'jid1-AVgCeF1zoVzMjA@jetpack.xpi',
            # 'cookies.sqlite')
            l = Link(profile_dir, home_dir, extension_name, cookie_name)
            self.origin_cookie = os.path.join(home_dir, "profile")
            self.origin_cookie = os.path.join(self.origin_cookie,
                                              str(self.profile_id))
            self.origin_cookie = os.path.join(self.origin_cookie, cookie_name)
            print "cookie_name:", self.origin_cookie
            l.link_ext("extensions", self.profile_id)
            l.link_cookie("", self.profile_id)
            l.link_prefs("", self.profile_id)

            # print self.origin_profile
            if self.is_debug_mode == 0:
                # fp = webdriver.FirefoxProfile(self.origin_profile)
                # fp = webdriver.FirefoxProfile()
                self.browser = webdriver.Firefox()
            else:
                if sys.platform == "win32":
                    self.browser = webdriver.Firefox()
                else:
                    # fp = webdriver.FirefoxProfile("/home/pi/.mozilla/firefox/q9wwlcky.default")
                    fp = webdriver.FirefoxProfile(profile_dir)
                    self.browser = webdriver.Firefox(fp)
            # self.browser.set_page_load_timeout(30)
            # self.browser = webdriver.Firefox(log_path='d:\\geckodriver.log')

            self.click_mode = ClickMode(self.browser, self.server_id, self.db,
                                        self.is_debug_mode,
                                        "d:\\selenium\\000.jb")
            self.input_mode = InputMode(self.browser)
            self.browser.maximize_window()
        except Exception, e:
            print "the webdriver config failed,{0}".format(e)
            traceback.print_exc()
            self.logger.error("the webdriver config failed,{0}".format(e))
            # 任务提供的profileid 的path为NULL
            self.set_task_status(9)
            self.update_task_allot_impl_sub()
            myprint.print_red_text(u"引擎:浏览器配置失败，检查下profileid的path")
            self.quit(0)
            self.q.put(0)
            sys.exit(1)

    def element(self, tag, locator):
        try:
            if tag is None:
                ele = self.Wait.until(
                    EC.presence_of_element_located((locator)))
            else:
                ele = self.Wait.until(
                    EC.presence_of_element_located((tag, locator)))
        except TimeoutException, e:
            self.logger.info("no such element:{0}".format(locator))
            raise NoSuchElementException(locator)
        return ele

    def element_all(self, tag, locator):
        try:
            if tag is None:
                divs = self.Wait.until(
                    EC.presence_of_all_elements_located((locator)))
            else:
                divs = self.Wait.until(
                    EC.presence_of_all_elements_located((tag, locator)))
        except TimeoutException, e:
            self.logger.info("no such element1:{0}".format(locator))
            raise NoSuchElementException(locator)

        return divs

    def is_element_stale(self, webelement):
        """

        Checks if a webelement is stale.

        @param webelement: A selenium webdriver webelement

        """
        try:
            webelement.tag_name
        except StaleElementReferenceException:
            print "element stale"
            return True
        except:
            pass

        return False

    def wait_util(self,
                  condition,
                  timeout=30,
                  sleep_time=0.5,
                  pass_exceptions=False,
                  message=None):
        # __check_condition_parameter_is_function(condition)

        last_exception = None
        end_time = datetime.now() + timedelta(seconds=timeout)
        while datetime.now() < end_time:
            try:
                if condition():
                    return
            except Exception as e:
                if pass_exceptions:
                    raise e
                else:
                    last_exception = e
            sleep(sleep_time)

    def baidu_search(self, keyword):
        print "get in baidu search"
        # threading.Thread(target=self.load_page_timeout).start()
        # self.browser.get("http://www.baidu.com")
        self.click_mode.signal_pausing()
        with self.wait_for_new_window(self.browser):
            self.browser.execute_script("window.open('http://www.baidu.com')")
        # self.switch_to_new_windows()  不能使用-1
        num = len(self.browser.window_handles)
        #firefox num+1
        print "winlen:", num
        self.browser.switch_to.window(
            self.browser.window_handles[self.win_pos])
        self.win_pos = self.win_pos + 1

        print "wait kw...."
        input_block = self.element(By.ID, "kw")
        print "wait kw finish...."
        keywords = keyword.split(",")
        for i in range(0, len(keywords)):
            self.input_mode.input(input_block, keywords[i], "kw")
            if i < len(keywords) - 1:
                pyautogui.press("enter")
                ran = random.randint(2, 3)
                sleep(ran)
        submit_button = self.element(By.XPATH, '''//*[@id="su"]''')
        left = self.browser.execute_script(
            '''function getElementViewLeft(element){var actualLeft=element.offsetLeft;var current=element.offsetParent;while(current!==null){actualLeft+=current.offsetLeft;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollLeft=document.body.scrollLeft}else{var elementScrollLeft=document.documentElement.scrollLeft}return actualLeft-elementScrollLeft};return getElementViewLeft(arguments[0])''',
            submit_button)
        top = self.browser.execute_script(
            '''function getElementViewTop(element){var actualTop=element.offsetTop;var current=element.offsetParent;while(current!==null){actualTop+=current.offsetTop;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollTop=document.body.scrollTop}else{var elementScrollTop=document.documentElement.scrollTop}return actualTop-elementScrollTop};return getElementViewTop(arguments[0])''',
            submit_button)
        step = random.randint(20, 100)
        left += step
        top += 100
        pyautogui.moveTo(left, top, duration=3)
        self.click_mode.signal_pausing()
        pyautogui.click()
        pyautogui.moveTo(800, 200, duration=3)
        self.click_mode.signal_pausing()
        pyautogui.click()

    def baidu_search_phone(self, keyword):
        try:
            self.click_mode.signal_pausing()
            self.browser.get('''https://m.baidu.com''')
            sleep(1)
            elename = ""
            try:
                input_block = self.Wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    "input#index-kw")))
                elename = "index-kw"
            except Exception, e:
                input_block = self.Wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,
                                                    "input#word")))
                elename = "word"
            randnum = random.randint(0, 1)
            if randnum == 0:
                print(u"输入法拼音")
                self.input_mode.input_pinyin(input_block, keyword,
                                             elename)  #"index-kw")
            elif randnum == 1:
                print(u"输入法五笔")
                self.input_mode.input_wubi(input_block, keyword,
                                           elename)  #"index-kw")

            sleep(2)
            input_block.send_keys(Keys.ENTER)
        except Exception, e:
            myprint.print_red_text(u"baidu_search_phone错误:{0}".format(str(e)))

    def satisfy_condition(self, block):
        if self.method == "url":
            a_tag = block.find_element_by_tag_name("a")
            link = a_tag.get_attribute("href")
            try:
                response = requests.get(link, timeout=5)
                result = response.url
                print result
            except Exception, e:
                myprint.print_red_text(e)
                result = None
            if result is None:
                return False
            if result.find(self.url) != -1:
                return True
            else:
                return False
        elif self.method == "title":
            if block.text.find(self.title) != -1:
                return True
            else:
                return False
        elif self.method == "showurl":
            try:
                a_tag = block.find_element_by_css_selector(".c-showurl")
                t = a_tag.text
                if t.find(self.url) != -1:
                    return True
                else:
                    return False
            except Exception, e:
                if self.is_ad == 0:
                    return False
                print u"########广告########"
                a_tag = block.find_element_by_css_selector("a:first-child")
                try:
                    link = a_tag.get_attribute("data-landurl")
                except Exception, e:
                    return False
                else:
                    if link is not None:
                        if link.find(self.url) != -1:
                            return True
                        else:
                            return False
                        print "###################"
                    else:
                        return False
            else:
                if a_tag is not None:
                    print a_tag.text
                    if a_tag.text.find(self.url) != -1:
                        return True
                    else:
                        return False

    def satisfy_condition_phone(self, block):
        try:
            h3_tag = block.find_element_by_tag_name("h3")
            a_tag = block.find_element_by_tag_name("a")
            link = a_tag.get_attribute("href")
            if self.method == "url":
                while True:
                    try:
                        response = requests.get(link)
                        result = response.text
                        break
                    except Exception, e:
                        myprint.print_red_text(e)
                re_result = re.search(r'window.location.replace\("(.*)"\)',
                                      result)
                if re_result is not None:
                    url_content = re_result.group(1)
                    myprint.print_red_text("############")
                    myprint.print_red_text(url_content)
                    myprint.print_red_text(h3_tag.text)
                    myprint.print_red_text("############")
                else:
                    return False
                if url_content == self.url:
                    return True
                else:
                    return False
            elif self.method == "title":
                if h3_tag.text.find(self.title) != -1:
                    return True
                else:
                    return False
            elif self.method == "showurl":
                try:
                    a_tag = block.find_element_by_css_selector("div.c-showurl")
                    if a_tag.text.find(self.url) != -1:
                        myprint.print_green_text(u'''找到链接标题:{0}'''.format(
                            a_tag.text))
                        return True
                    else:
                        return False
                except Exception, e:
                    print(str(e))
                    return False
            else:
                if a_tag is not None:
                    print a_tag.text
                    if a_tag.text.find(self.title) != -1:
                        myprint.print_green_text(u'''找到链接标题:{0}'''.format(
                            a_tag.text))
                        return True
                    else:
                        return False
        except Exception, e:
            myprint.print_red_text(e)
            return False

    def click_next_btn_phone(self, title):
        title.location_once_scrolled_into_view
        #drawSquare()
        #a_tag = title.find_element_by_css_selector("a.new-nextpage")
        print title.get_attribute("href")
        left = self.browser.execute_script(
            '''function getElementViewLeft(element){var actualLeft=element.offsetLeft;var current=element.offsetParent;while(current!==null){actualLeft+=current.offsetLeft;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollLeft=document.body.scrollLeft}else{var elementScrollLeft=document.documentElement.scrollLeft}return actualLeft-elementScrollLeft};return getElementViewLeft(arguments[0])''',
            title)
        top = self.browser.execute_script(
            '''function getElementViewTop(element){var actualTop=element.offsetTop;var current=element.offsetParent;while(current!==null){actualTop+=current.offsetTop;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollTop=document.body.scrollTop}else{var elementScrollTop=document.documentElement.scrollTop}return actualTop-elementScrollTop};return getElementViewTop(arguments[0])''',
            title)
        # 修正位置
        top += 125
        left += 40
        pyautogui.moveTo(left, top, duration=6)
        self.click_mode.signal_pausing()
        pyautogui.click()
        sleep(10)

    def get_element_height(self, ele):
        return ele.size['height']

    #  h = self.browser.execute_script('''function getElementHeight(element){return element.clientHeight;};return getElementHeight(arguments[0]);''',ele)
    def get_element_width(self, ele):
        return ele.size['width']
        #h = self.browser.execute_script('''function getElementWidth(element){return element.clientWidth;};return getElementWidth(arguments[0]);''',ele)

    def process_block(self, title, offtop=0):
        try:
            try:
                a_tag = title.find_element_by_tag_name("a")
            except Exception, e:
                a_tag = title  #因为有可能div里找不到a 所以直接点击整个div
            print("1")
            self.browser.execute_script(
                "return arguments[0].scrollIntoView();", title)
            sleep(1)
            # w, h =  GetTitleDimensions(a_tag.text)
            w = self.get_element_width(a_tag)
            h = self.get_element_height(a_tag)
            availHeight = self.browser.execute_script(
                "return window.document.documentElement.clientHeight;")
            top = self.browser.execute_script(
                '''function getElementViewTop(element){var actualTop=element.offsetTop;var current=element.offsetParent;while(current!==null){actualTop+=current.offsetTop;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollTop=document.body.scrollTop}else{var elementScrollTop=document.documentElement.scrollTop}return actualTop-elementScrollTop};return getElementViewTop(arguments[0])''',
                title)
            if top < 200:  #位置太高，有可能被挡到，#先滚到最顶部，再移动标题处，再向下滚200
                self.browser.execute_script("window.scrollBy(0, 0);")
                self.browser.execute_script(
                    "return arguments[0].scrollIntoView();", title)
                self.browser.execute_script("window.scrollBy(0, -200);")
            #drawSquare()
            try:
                a_tag = title.find_element_by_css_selector("a:first-child")
            except Exception, e:
                a_tag = title
            print a_tag.get_attribute("href")
            left = self.browser.execute_script(
                '''function getElementViewLeft(element){var actualLeft=element.offsetLeft;var current=element.offsetParent;while(current!==null){actualLeft+=current.offsetLeft;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollLeft=document.body.scrollLeft}else{var elementScrollLeft=document.documentElement.scrollLeft}return actualLeft-elementScrollLeft};return getElementViewLeft(arguments[0])''',
                title)
            top = self.browser.execute_script(
                '''function getElementViewTop(element){var actualTop=element.offsetTop;var current=element.offsetParent;while(current!==null){actualTop+=current.offsetTop;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollTop=document.body.scrollTop}else{var elementScrollTop=document.documentElement.scrollTop}return actualTop-elementScrollTop};return getElementViewTop(arguments[0])''',
                title)
            #用script首页后,之后继续打开可能会出现窗口数更之前一样,导致wait超时
            self.click_mode.signal_pausing()
            print(w)
            print(h)
            w_a = random.randint(1,int(w))
            h_a = random.randint(2,int(h-2))
            print("top:{0} left:{1} w:{2} h:{3} h_a:{4} w_a:{5}".format(top,left,w,h,h_a,w_a))
            self.click_mode.click(top+h_a+offtop, left+w_a, a_tag,g_step-10, self.cm)
            sleep(3)
            return 0
        except Exception, e:
            myprint.print_red_text(u"点击出错:" + str(e))
            sleep(5)
            return -1

    def move_to_next_btn(self, ele, step=g_step, p_ctrl=False):
        availHeight = self.browser.execute_script(
            "return window.document.documentElement.clientHeight;")
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
        self.click_mode.signal_pausing()
        self.click_mode.click(top, left, ele, 0, 2, p_ctrl)

    def get_page_ele(self, num):
        for i in range(5):
            try:
                selector = "a>span.pc"
                divs = self.element_all(By.CSS_SELECTOR, selector)
                stale = False
                print "*********find a>span.pc**********"
                #  self.browser.execute_script(
                #      "window.scrollTo(0,document.body.scrollHeight)")
                self.go_to_page_bottom()
                for a in divs:
                    print "link text:", a.text
                    if a.text == str(num).strip():
                        return a  #True
                #may is no clicable
                # xpath = "//*[@id='page']/strong/span[%d]"%(num)
                # selector = "#page > strong > span.pc"
                # divs = self.element_all(By.CSS_SELECTOR, selector)
                # # divs = self.element_all(By.XPATH, xpath)
                # print "*********",selector,"**********"
                # self.browser.execute_script(
                #     "window.scrollTo(0,document.body.scrollHeight)")
                # for a in divs:
                #     print "not clicakble link text:",a.text
                #     if a.text == str(num).strip():
                #         return a #True
            except StaleElementReferenceException, e:
                myprint.print_red_text("stale retry4")
                continue

    def go_to_page_bottom(self):  #拉到网页最低部，慢慢滚动，不能一下子滚到最下面
        try:
            h = self.browser.execute_script("return document.body.clientHeight"
                                            )  #document.body.scrollHeight")
            sh = 0
            while 1:
                scroll_h = random.randint(50, 200)
                sh += scroll_h
                self.browser.execute_script(
                    "window.scrollTo(0,{0})".format(sh))
                h = h - scroll_h
                if h < 0:
                    break
                wt = random.randint(0, 10)
                sleep(wt / 10)
            return 0
        except Exception, e:
            self.logger.error(u"网页向下滚动时出错:" + str(e))
            return -1

    def go_to_next_page(self, num=0):
        stale = True
        for i in range(0, 5):
            # while stale:
            if stale:
                try:
                    if num == 0:
                        selector = "a.n"
                        a_list = self.element_all(By.CSS_SELECTOR, selector)
                        stale = False
                        print "*********find a.n**********"
                        #   self.browser.execute_script(
                        #       "window.scrollTo(0,document.body.scrollHeight)")
                        self.go_to_page_bottom()  #一点点向下滚动到最下面
                        for a in a_list:
                            if a.text == u"下一页>":
                                self.move_to_next_btn(a, 100)
                                return a
                    else:
                        print "jump in next page.."
                        selector = "a>span.pc"
                        divs = self.element_all(By.CSS_SELECTOR, selector)
                        stale = False
                        print "*********find a>span.pc**********"
                        #  self.browser.execute_script(
                        #      "window.scrollTo(0,document.body.scrollHeight)")
                        self.go_to_page_bottom()
                        for a in divs:
                            print "link text:", a.text
                            if a.text == str(num):
                                self.move_to_next_btn(a, 100)
                                return a  #True
                    sleep(3)
                    continue
                except StaleElementReferenceException, e:
                    myprint.print_red_text("stale retry1")
                    stale = True
                    continue
            break
        return None  #False

    def go_to_next_page_phone(self):
        #self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        self.go_to_page_bottom()
        sleep(4)
        page_source = self.browser.page_source
        next_page_link = None
        if page_source.find("class=\"new-nextpage\"") != -1:
            next_page_link = self.browser.find_element_by_css_selector(
                "a.new-nextpage")
        elif page_source.find("class=\"new-nextpage-only\"") != -1:
            next_page_link = self.browser.find_element_by_css_selector(
                "a.new-nextpage-only")
        if next_page_link is not None:
            self.click_next_btn_phone(next_page_link)
            return True
        else:
            return False

    def is_url_ok(self):  #判断是否打开的网页是正确的
        try:
            if self.real_url == "":
                myprint.print_green_text(u"real_url为空，无法判断目标是否正确")
                return 0
            if self.method == "title":
                myprint.print_green_text(u"搜索类型是‘标题’,无法判断目标URL")
                return 0
            selector = "a"
            sleep(5)
            self.switch_to_new_windows()
            #a_tags = self.element_all(By.TAG_NAME, selector)
            cur_url = self.browser.current_url
            myprint.print_blue_text(u"当前打开的目标网址为:{0}".format(cur_url))

            if cur_url.find(self.real_url) != -1:
                myprint.print_green_text(u"目标URL正确")
                return 0
            else:
                myprint.print_green_text(u"目标URL错误")
                print(u"当前URL：" + cur_url)
                print(u"目标URL:" + self.real_url)
                sleep(10)
                return -1
        except Exception, e:
            self.logger.error(u"判断目标URL时 错误:" + str(e))
            return -1

    def baiduSearchPhone(self):
        myprint.print_green_text(u"引擎:开始进去手机百度")
        self.baidu_search_phone(self.keyword)
        sleep(5)
        myprint.print_green_text(u"引擎:开始搜索标题")
        count = 1
        # self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        while True:
            if count == self.total_page:
                myprint.print_red_text(u"已到达搜索上限页数, 开始退出")
                return 2
        #  self.browser.execute_script(
        #      "window.scrollTo(0,document.body.scrollHeight)")
            self.go_to_page_bottom()
            sleep(4)
            myprint.print_green_text(u"引擎:开始第{page}页搜索".format(page=count))
            try:
                divs = self.Wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                         "div.c-container")))
            except Exception, e:
                divs = self.Wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                         "div.abs")))  #有时候是这个

            for div in divs:
                # if random.random() < 0.2:
                #     self.process_block(div)
                if self.satisfy_condition_phone(div):
                    rt = self.process_block(div, 8)
                    if rt == 0:
                        rt = self.is_url_ok()
                        if rt == 0:
                            return 1
                        else:
                            return 3
                    else:
                        return -1
            count = count + 1
            myprint.print_green_text(
                u"引擎:第{page}页搜索失败!尝试进入下一页".format(page=count))
            ret = self.go_to_next_page_phone()

            if not ret:
                print(u"当前第{0}页，下一页按钮为空".format(count))
                return 2
            myprint.print_green_text(u"引擎:成功进入下一页")

    def handle_page(self, count):
        stale = True
        for i in range(0, 5):
            # while stale:
            if stale:
                # if True:
                try:
                    if self.onlysearch == 0:
                        if self.method == "showurl":
                            titles = []
                            adsdiv = []
                            divs = self.element_all(By.CSS_SELECTOR,
                                                    "div.c-container")
                            stale = False
                            for div in divs:
                                # try:
                                if True:
                                    title = div.find_element_by_tag_name("h3")
                                    if title is not None:
                                        titles.append(title.text)
                                        # print title.text

                            odivs = self.element_all(By.CSS_SELECTOR, "h3.t")
                            for div in odivs:
                                # print "div.txt",div.text
                                if div.text not in titles:
                                    # print titles
                                    # print div.text
                                    if self.satisfy_condition(div):
                                        rt = self.process_block(div)
                                        if rt == 0:
                                            rt = self.is_url_ok()
                                            if rt == 0:
                                                return 0
                                            else:
                                                return 3  #打开的网页非目标页，可能是因为点击错误
                                        else:
                                            return -1
                        else:
                            divs = self.Wait.until(
                                EC.presence_of_all_elements_located(
                                    (By.CSS_SELECTOR, "h3.t")))
                        for div in divs:
                            if self.satisfy_condition(div):
                                rt = self.process_block(div)
                                if rt == 0:
                                    rt = self.is_url_ok()
                                    if rt == 0:
                                        return 0
                                    else:
                                        return 3  #打开的网页非目标页，可能是因为点击错误
                                else:
                                    return -1
                    return -1
                except StaleElementReferenceException, e:
                    myprint.print_red_text("stale retry2")
                    stale = True
                    continue

                except NoSuchElementException, e:
                    myprint.print_red_text(u"进入下一页错误,刷新:{0}".format(e))
                    self.logger.error(u"进入下一页错误,刷新:{0}".format(e))
                    return -1
            break

        return -1

    def jump_to_startpage(self, nums):
        for i in nums:
            # 第一页 跳转会导致滚动，无法定位到页首元素
            print "num:", i
            if int(i) <= 1:
                return
            ele = self.go_to_next_page(i)
            self.Wait.until(ele_not_clickable(i))

    def baiduSearch(self):
        # nums = [3,4,7,10]
        myprint.print_green_text(u"引擎:开始进入百度搜索")
        self.baidu_search(self.keyword)
        myprint.print_green_text(u"引擎:开始搜索标题")
        print "start jump to startpage..."
        if self.start_search_page:
            nums = self.start_search_page.split(",")
            if nums:
                print "nums:", nums
                self.jump_to_startpage(nums)
        print "jump to startpage finished ..."
        count = 1
        startpage = 1
        if nums:
            startpage = int(nums[-1])
            if startpage == 0:
                count = 1
                startpage = 1
        pagenum = 0
        while True:
            if count >= self.total_page:
                myprint.print_red_text(u"已到达搜索上限页数, 开始退出")
                if self.onlysearch == 0:
                    return 2
                else:
                    return 0
            myprint.print_green_text(u"引擎:开始第{page}页搜索".format(page=count))
            # sleep(5)
            pagenum = startpage + count
            ret = self.handle_page(pagenum)
            if ret == 0:
                return 1
            elif ret == 3:  #有找到并点击进去，但打开后的页面不是指定的目标页面，可能是点击错
                return 3
            myprint.print_green_text(
                u"引擎:第{page}页搜索失败!尝试进入下一页".format(page=pagenum))
            count = count + 1
            ret = self.go_to_next_page()

            print "start wait"
            self.Wait.until(ele_not_clickable(pagenum))
            print count, "wait over"

            if not ret:
                return 0
            myprint.print_green_text(u"引擎:成功进入下一页")
        return 1

    def __del__(self):
        self.browser.quit()

    def update_search_times(self):
        myprint.print_green_text(u"引擎:检查失败搜索次数是否超过设置次数")
        sql = "select search_times - had_search_times times from baiduSearch where id = {id}".format(
            id=self.id)
        ret = self.db.select_sql(sql, 'DictCursor')
        if ret[0]['times'] <= 0:
            myprint.print_green_text(u"引擎:任务失败搜索次数超过设置次数,vm_task设置status为0")
            updatesql = """update vm_task set status = 0 where id in (select taskid from baiduSearchIdMap where search_id = {id})""".format(
                id=self.id)
        else:
            myprint.print_green_text(u"引擎:添加失败搜索次数")
        updatesql = "update baiduSearch set had_search_times = had_search_times + 1 where id = {id}".format(
            id=self.id)
        updateret = self.db.execute_sql(updatesql)

    @contextmanager
    def wait_for_new_window(self, driver, timeout=20):
        handles_before = driver.window_handles
        print "len:", len(handles_before)
        yield
        WebDriverWait(driver, timeout).until(
            lambda driver: len(handles_before) != len(driver.window_handles))

    @contextmanager
    def wait_for_page_load(self, timeout=10):
        old_page = self.browser.find_element_by_tag_name('html')
        print "old_page.id", old_page.id
        # print "old_page.session" , old_page.session
        print old_page
        yield
        WebDriverWait(self.browser, timeout).until(staleness_of(old_page))
        print "page loaded"

    def taskshot_and_upload(self):
        try:
            selector = "a"
            self.switch_to_new_windows()
            sleep(10)
         #   randa = random.choice(a_tags)
         #   index = 0
         #   while not randa.is_displayed():
         #       print(u"not randa.is_displayed {0}".format(index))
         #       index += 1
         #       sleep(1)
         #       if index > 20:
         #           break
         #   if randa.is_displayed():
            print(u"---》开始截图《---")
            localfile = "D:\\{0}.jpg".format(self.rid)
            # localfile = "d:\\task.jpg"
            print localfile
            ss = ScreenShot(localfile)
            ss.take()
            print "taked"
            ftp = PicFTP('192.168.1.53', 21, 'uppic', '123456',
                        self.logger, self.server_id, self.vm_id)
            ftp.login()
            ftp.upload_task_file(self.task_id, self.rid, localfile)
            os.remove(localfile)
            print(u"截图成功")

        except Exception, e:
            print(u"截图出错" + str(e))
            traceback.print_exc()
            print "rand click excpetion", e
            pass

    def after_finish_search_task(self):
        #wait_function = [self.scroll_windows, self.random_click]
        self.main_win = self.browser.window_handles[-1]

        wait_function = [self.random_click]
        self.task_finished()
        if sys.platform == 'win32':
            self.browser.switch_to.window(self.main_win)
            print "==========screen shot=========="
            self.taskshot_and_upload()

        wait_time = self.standby_time * 60 + 10 + time()
        times = random.randint(3, 5)
        while wait_time > time():
            myprint.print_green_text(u"引擎:等待状态,距离完成还有:{wait_time}秒".format(
                wait_time=int(wait_time - time())))
            if self.random_event_status == 1:
                if self.onlysearch == 0:
                    if self.random_event_count < times:
                        wait_function[random.randint(0,
                                                     len(wait_function) - 1)]()
                        self.random_event_count = self.random_event_count + 1
                    else:
                        myprint.print_green_text(u"引擎:随机事件次数已经达到上限")
            sleep(10)
        self.task_wait_finished()
        self.quit()  # 浏览器退出

    def run(self):
        for i in range(0, 1):
            try:
                if self.terminal_type == 2:
                    ret = self.baiduSearchPhone()
                    if ret == 1:
                        self.after_finish_search_task()
                    elif ret == 2:
                        myprint.print_red_text(u"引擎:搜索失败, 一到最后一页")
                        self.logger.error(u"搜到到最后一任务状态改11")
                        self.set_task_status(11)
                        self.update_search_times()
                        self.update_task_allot_impl_sub()
                        self.quit(0)
                    elif ret == 3:
                        myprint.print_red_text(u"引擎:打开的网页非目标页面")
                        self.logger.error(u"打开的网页非目标页面状态改12")
                        self.set_task_status(12)
                        self.update_search_times()
                        self.update_task_allot_impl_sub()
                        self.quit(0)
                    else:
                        myprint.print_red_text(u"引擎:搜索失败, 没有找到目标")
                        self.logger.error(u"搜索不到目标，任务状态改为8")
                        self.set_task_status(8)
                        self.update_search_times()
                        self.update_task_allot_impl_sub()
                        self.quit(0)
                    return True
                elif self.terminal_type == 1 or self.terminal_type == 3:
                    ret = self.baiduSearch()
                    if ret == 1:
                        self.after_finish_search_task()
                    elif ret == 2:
                        myprint.print_red_text(u"引擎:搜索失败, 一到最后一页")
                        self.logger.error(u"搜到到最后一任务状态改11")
                        self.set_task_status(11)
                        self.update_search_times()
                        self.update_task_allot_impl_sub()
                        self.quit(0)
                    elif ret == 3:
                        myprint.print_red_text(u"引擎:打开的网页非目标页面")
                        self.logger.error(u"打开的网页非目标页面状态改12")
                        self.set_task_status(12)
                        self.update_search_times()
                        self.update_task_allot_impl_sub()
                        self.quit(0)
                    else:
                        myprint.print_red_text(u"引擎:搜索失败, 没有找到目标")
                        self.logger.error(u"搜索不到目标，任务状态改为8")
                        self.set_task_status(8)
                        self.update_search_times()
                        self.update_task_allot_impl_sub()
                        self.quit(0)
                    return True
            except NoSuchElementException, e:
                myprint.print_red_text(u"找不到对应元素:{0}".format(e))
                traceback.print_exc()
                # self.task_failed(8)
                redo = True
                # continue
                # return False
            except TimeoutException, e:
                myprint.print_red_text(u"超时,找不到对应元素2:{0}".format(e))
                traceback.print_exc()
                # self.task_failed(8)
                redo = True
                # continue
                # return False
            except WebDriverException, e:
                myprint.print_red_text(u"超时,找不到对应元素3:{0}".format(e))
                traceback.print_exc()
                # self.task_failed(8)
                redo = True
                # continue
            traceback.print_exc()
            myprint.print_red_text(u"引擎遇到错误:可能是网速过慢或者网络中断")
            self.update_search_times()
            self.update_task_allot_impl_sub()
            self.task_failed()
            self.quit(0)
            return False

    def scroll_windows(self):
        myprint.print_green_text(u"引擎:尝试滚动滑动条")
        self.switch_to_new_windows()
        if random.random() > 0.5:
            #   self.browser.execute_script(
            #       "window.scrollTo(0,document.body.scrollHeight)")
            self.go_to_page_bottom()
        else:
            self.browser.execute_script("window.scrollTo(0,0)")

    def random_click(self):
        if self.cm == 0:
            return
        myprint.print_green_text(u"引擎:尝试随机点击")
        self.browser.switch_to.window(self.main_win)
        # self.switch_to_new_windows()

        # a_tags = self.browser.find_elements_by_css_selector("a>img")
        try:
            selector = "a>img"
            a_tags = self.element_all(By.CSS_SELECTOR, selector)
            randa = random.choice(a_tags)
            while randa.is_displayed():
                randa.location_once_scrolled_into_view
                #快捷键操作
                action = ActionChains(self.browser)
                # elem = driver.find_element_by_link_text("Gmail")
                self.click_mode.signal_pausing()
                action.move_to_element(randa).key_down(
                    Keys.CONTROL).click(randa).key_up(Keys.CONTROL).perform()
                # self.process_block(randa)
                #移动点击
                # self.move_to_next_btn(randa, g_step, True)
                # randa.click()
                break
        except Exception, e:
            traceback.print_exc()
            print "rand click excpetion", e
            pass

    def switch_to_new_windows(self):
        myprint.print_green_text(u"引擎:切换标签")
        sleep(1)
        windows = self.browser.window_handles
        self.browser.switch_to.window(windows[-1])

    def load_page_timeout(self):
        sleep(30)
        # if True:
        if self.loadstatus:
            # print "timeout and refresh"
            # pyautogui.press('f5')
            self.q.put(0)
            self.set_task_status(10)
            self.browser.quit()
            os._exit(1)

    def quit(self, bcopy=1):
        print("quit")
        self.browser.get("about:support")
        # self.browser.get("about:blank")
        sleep(3)
        for i in range(1, 2):
            try:
                profiletmp = self.browser.execute_script(
                    '''let currProfD = Services.dirsvc.get("ProfD", Ci.nsIFile);
                    let profileDir = currProfD.path;
                    return profileDir

                    ''')
                cookietmp = os.path.join(profiletmp, cookie_name)
                origin_cookie = os.path.join(home_dir, "profile")
                origin_cookie = os.path.join(origin_cookie, str(
                    self.profile_id))
                origin_cookie = os.path.join(origin_cookie, cookie_name)

                if self.copy_cookie == 1 and bcopy == 1:
                    if sys.platform == 'win32':
                        if os.system("XCOPY /E /Y /C " + profiletmp + "\*.* " +
                                     self.origin_profile):
                            print "files should be copied :/"
                    else:
                        if os.system(
                                "cp " + cookietmp + " " + self.origin_cookie):
                            print "files should be copied :/"
                    sleep(4)
                # self.browser.quit()
                # shutil.rmtree(profiletmp, True)
                break
            except Exception, e:
                '''sometime cannt found services'''
                traceback.print_exc()
                sleep(5)
                continue
        self.browser.quit()
        sleep(6)
        if profiletmp is not None:
        	shutil.rmtree(profiletmp, True)
            

def get_ip(db, serverid):  # 取得当前IP地址
    sql = "select ip from vpn_status where serverid={0}".format(serverid)
    print(sql)
    res = db.select_sql(sql, 'DictCursor')
    if res == None:
        return ""
    else:
        return res[0]["ip"]


def write_ip_to_vm_cur_task(db,taskid, serverid):  # 写入到vm_cur_task里
    ip = get_ip(db, serverid)
    #ip='127.0.0.1'
    sql = "update vm_cur_task set ip='{0}' where id={1}".format(ip,taskid)
    print(sql)
    ret = db.execute_sql(sql)
    if ret < 0:
        print(u"写入运行时IP出错")
        return -1
    return 0


def is_ad_task(db, id):
    sql = '''select is_ad from vm_task where id={0}'''.format(id)
    res = db.select_sql(sql)
    if not res or len(res) == 0:
        return None
    is_ad = res[0][0]
    return is_ad


def get_task(db, id):
    myprint.print_green_text(u"获取任务中")
    sql = '''select t3.*,t1.id as rid,t1.server_id as server_id,t1.cur_task_id as cur_task_id from vm_cur_task t1 INNER JOIN baiduSearchIdMap t2
      on t1.cur_task_id = t2.taskid LEFT JOIN baiduSearch t3 on t3.id = t2.search_id
      where t1.id = {id}  and t3.status = 1'''.format(id=id)
    res = db.select_sql(sql, 'DictCursor')
    if not res or len(res) == 0:
        myprint.print_green_text(u"没有获取到任务")
        return None
    #排名按服务器ID，找出start_search_page
    baidu_search_id = res[0]["id"]
    serverid = res[0]["server_id"]
    search_rank = res[0]["search_rank"]
    if search_rank == 1:  #不用搜索的不在baiduSearch_rank里，须要在baiduSearch里找
        pass
    else:
        sql = """select start_search_page from baiduSearch_rank where baiduSearch_id={0} and server_id={1}""".format(
            baidu_search_id, serverid)
        res_start_page = db.select_sql(sql, 'DictCursor')
        if not res_start_page or len(res_start_page) == 0:
            myprint.print_red_text(
                u"baiduSearch_rank没有获取到跳转页,用baiduSearch的跳转页,出错因为baiduSearch增加新记录但没运行搜索排名程序所以baiduSearch_rank找不到排名"
            )
        else:
            res[0]["start_search_page"] = res_start_page[0][
                "start_search_page"]

    print(u"页数为：" + res[0]["start_search_page"])
    myprint.print_green_text(u"获取到{length}个任务".format(length=len(res)))
    for v in res:
        task_id = v['cur_task_id']
        is_ad = is_ad_task(db, task_id)
        v['keyword'] = v['keyword'].decode("utf8")
        v['title'] = v['title'].decode("utf8")
        v['area'] = v['area'].decode("utf8")
        v['url'] = v['url'].decode("utf8")
        print(u"URL为：{0}".format(v['url']))
        v['is_ad'] = is_ad

    return res


def init():
    myprint.print_green_text(u"bdads.py 2018/06/09 程序初始化中..")
    global taskid, is_debug_mode
    parser = optparse.OptionParser()
    parser.add_option("-t", "--task_id", dest="taskid")
    parser.add_option("-d", "--debug_mode", dest="is_debug", default="0")
    (options, args) = parser.parse_args()
    taskid = options.taskid
    is_debug_mode = int(options.is_debug)

    myprint.print_green_text(
        u"程序初始化完成, 获取到任务id:{id}".format(id=options.taskid))


def configdb(dbname):
    logging.config.fileConfig("{0}/log_conf/6avideo.log.conf".format(workpath))
    logger = logging.getLogger()
    cf = ConfigParser.ConfigParser()
    confpath = "{0}/log_conf/db.conf".format(workpath)
    cf.read(confpath)
    db_host = cf.get(dbname, "db_host")
    db_name = cf.get(dbname, "db_name")
    db_user = cf.get(dbname, "db_user")
    db_pwd = cf.get(dbname, "db_pwd")
    db_charset = cf.get(dbname, "db_charset")
    db = dbutil.DBUtil(logger, db_host, 3306, db_name, db_user, db_pwd,
                       db_charset)
    global profile_dir, home_dir, extension_name, cookie_name
    profile_dir = cf.get('ENV', "profile_dir")
    home_dir = cf.get('ENV', "home_dir")
    extension_name = cf.get('ENV', "extension_name")
    cookie_name = cf.get('ENV', "cookie_name")
    print profile_dir, home_dir, extension_name, cookie_name
    return db, logger


def main():
    init()
    q = Queue.Queue()
    db, logger = configdb("DB_vm")
    pids = psutil.pids()

    try:
        # if True:
        res = get_task(db, taskid)
        if res != None:
            write_ip_to_vm_cur_task(db, taskid,res[0]["server_id"])#写入IP res[0]["server_id"]
            for t in res:
                c_rate = t['click_rate']
                cr = ClickRate(c_rate)
                cm = cr.be_click_or_not()
                is_ad = t['is_ad']

                if t['method'] == None:
                    t['method'] = "url"
                format_data = {
                    'keyword': t['keyword'],
                    'title': t['title'],
                    'url': t['url'],
                    'method': t['method'],
                    'script_name': t['script_name'],
                    'onlysearch': t['onlysearch'],
                    'click_mode': cm,
                    'is_ad': t['is_ad']
                }

                myprint.print_green_text(u'''



                    开始执行任务:



                    关键词:{keyword},



                    标题:{title},



                    链接:{url},



                    是否点击:{click_mode},
                    内页脚本:{script_name},
                    广告任务:{is_ad}'''.format(**format_data))

                myprint.print_green_text(u"===========提交引擎初始化中===========")
                engine = ChinaUSearch(logger, db, taskid, q, pids, t, cm,
                                      is_ad, is_debug_mode)
                if engine.run():
                    q.put(1)
                    myprint.print_red_text(u"引擎:任务成功")
                else:
                    q.put(0)
                    myprint.print_red_text(u"引擎:任务失败")
        else:
            logger.error(u"没有获取到任务")
    except Exception, e:
        myprint.print_red_text(u"引擎遇到错误:可能是网速过慢或者网络中断")
        q.put(0)
        traceback.print_exc()
        engine.task_failed()
        logger.error(u"引擎:搜索失败 {0}".format(e))
        myprint.print_red_text(u"引擎:搜索失败")


if __name__ == "__main__":
    #  if len(sys.argv) == 0:
    #      os.system('python27 -t 3513759 -d 1')
    main()
