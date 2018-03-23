#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from click_mode import ClickMode
from click_rate import ClickRate
from ColorPrint import Color
from input_mode import InputMode
from prototypecopy import prototype

from pypinyin import Style, lazy_pinyin, pinyin
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

myprint = Color()
workpath = os.getcwd()


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
    def __init__(self, logger, db, task_id, q, pids, task, cm, is_debug_mode):
        myprint.print_green_text(u"引擎:初始化本体")
        super(ChinaUSearch, self).__init__(logger, db, task_id, q, pids, cm,
                                           is_debug_mode)
        self.script_name = task["script_name"]
        self.title = task["title"]
        self.keyword = task["keyword"]
        self.url = task["url"]
        self.id = task["id"]
        self.method = task["method"]
        self.random_event_status = task['random_event_status']
        self.total_page = task['total_page']
        self.start_search_page = task['start_search_page']
        self.terminal_type = task["terminal_type"]  # 终端
        self.profile_type = task["terminal_type"]
        self.onlysearch = task["onlysearch"]
        self.random_event_count = 0
        self.module = importlib.import_module(
            "script.{script_name}".format(script_name=self.script_name))
        self.loadstatus = True
        myprint.print_green_text(u"引擎:初始化本体成功")
        myprint.print_green_text(u"引擎:初始化浏览器")
        self.webdriver_config()
        self.Wait = WebDriverWait(self.browser, 10)
        myprint.print_green_text(u"引擎:初始化浏览器成功")

    def webdriver_config(self):
        try:
            mapping = {"1": ".pc", "2": ".wap"}
            sql = "select path from profiles where id = {profile_id}".format(
                profile_id=self.profile_id)
            res = self.db.select_sql(sql, 'DictCursor')
            if res is None or len(res) == 0:
                self.logger.error("can't get information profile_path")
            self.origin_profile = res[0]['path']
            print self.origin_profile
            if self.is_debug_mode == 0:
                fp = webdriver.FirefoxProfile(self.origin_profile)
                # fp = webdriver.FirefoxProfile()
                self.browser = webdriver.Firefox(fp)
            else:
                if sys.platform == "win32":
                    self.browser = webdriver.Chrome()
                else:
                    self.browser = webdriver.Firefox()
            # self.browser = webdriver.Firefox(log_path='d:\\geckodriver.log')

            self.click_mode = ClickMode(self.browser, self.is_debug_mode,
                                        "d:\\selenium\\000.jb")
            self.input_mode = InputMode(self.browser)
            self.browser.maximize_window()
        except Exception, e:
            print "the webdriver config failed,{0}".format(e)
            traceback.print_exc()
            self.logger.error("the webdriver config failed,{0}".format(e))
            # 任务提供的profileid 的path为NULL
            self.set_task_status(9)
            myprint.print_red_text(u"引擎:浏览器配置失败，检查下profileid的path")
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
                    EC.presence_of_all_element_located((locator)))
            else:
                divs = self.Wait.until(
                    EC.presence_of_all_elements_located((tag, locator)))
        except TimeoutException, e:
            self.logger.info("no such element1:{0}".format(locator))
            raise NoSuchElementException(locator)

        return divs

    def baidu_search(self, keyword):
        threading.Thread(target=self.load_page_timeout).start()
        self.browser.get('''http://www.baidu.com''')
        self.loadstatus = False
        input_block = self.element(By.ID, "kw")
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
        pyautogui.click()
        pyautogui.moveTo(800, 200, duration=3)
        pyautogui.click()

    def baidu_search_phone(self, keyword):
        self.browser.get('''http://m.baidu.com''')
        sleep(1)
        input_block = self.Wait.until(
            EC.presence_of_element_located((By.ID, "index-kw")))
        randnum = random.randint(0, 1)
        if randnum == 0:
            self.input_pinyin(input_block, keyword, "kw")
        elif randnum == 1:
            self.input_wubi(input_block, keyword, "kw")

        input_block.send_keys(Keys.ENTER)
        sleep(2)

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
            except Exception, e:
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
                    # print a_tag.text
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
        except Exception, e:
            myprint.print_red_text(e)
            return False

    def process_block_phone(self, title):
        title.location_once_scrolled_into_view
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
        top += 125
        left += 40
        pyautogui.moveTo(left, top, duration=6)
        pyautogui.click()
        sleep(10)

    def process_block(self, title):
        availHeight = self.browser.execute_script(
            "return window.document.documentElement.clientHeight;")
        top = self.browser.execute_script(
            '''function getElementViewTop(element){var actualTop=element.offsetTop;var current=element.offsetParent;while(current!==null){actualTop+=current.offsetTop;current=current.offsetParent}if(document.compatMode=="BackCompat"){var elementScrollTop=document.body.scrollTop}else{var elementScrollTop=document.documentElement.scrollTop}return actualTop-elementScrollTop};return getElementViewTop(arguments[0])''',
            title)
        if top > availHeight:
            self.browser.execute_script(
                "return arguments[0].scrollIntoView();", title)
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
        self.click_mode.click(top, left, a_tag, 110, self.cm)

    def move_to_next_btn(self, ele, step=110, p_ctrl=False):
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
        self.click_mode.click(top, left, ele, 0, 2, p_ctrl)
        # pyautogui.moveTo(left, top, duration=1)
        # pyautogui.click()
        # sleep(3)

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
                        self.browser.execute_script(
                            "window.scrollTo(0,document.body.scrollHeight)")
                        for a in a_list:
                            if a.text == u"下一页>":
                                self.move_to_next_btn(a, 100)
                                return True
                    else:
                        print "jump in next page.."
                        selector = "a>span.pc"
                        divs = self.element_all(By.CSS_SELECTOR, selector)
                        stale = False
                        print "*********find a>span.pc**********"
                        self.browser.execute_script(
                            "window.scrollTo(0,document.body.scrollHeight)")
                        for a in divs:
                            # print a.text
                            if a.text == str(num):
                                self.move_to_next_btn(a, 100)
                                return True
                except StaleElementReferenceException, e:
                    myprint.print_red_text( "stale retry1")
                    stale = True
                    continue
            break
        return False

    def go_to_next_page_phone(self):
        self.browser.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
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
            self.browser.execute_script("arguments[0].click()", next_page_link)
            return True
        else:
            return False

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
                return False
            self.browser.execute_script(
                "window.scrollTo(0,document.body.scrollHeight)")
            sleep(4)
            myprint.print_green_text(u"引擎:开始第{page}页搜索".format(page=count))
            divs = self.Wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                     "div.c-container")))
            for div in divs:
                # if random.random() < 0.2:
                #     self.process_block(div)
                if self.satisfy_condition_phone(div):
                    self.process_block_phone(div)
                    return True
            count = count + 1
            myprint.print_green_text(
                u"引擎:第{page}页搜索失败!尝试进入下一页".format(page=count))
            ret = self.go_to_next_page_phone()

            if not ret:
                return False
            myprint.print_green_text(u"引擎:成功进入下一页")

    def handle_page(self, count):
        stale = True
        for i in range(0, 5):
            # while stale:
            if stale:
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
                                        self.process_block(div)
                                        return True
                        else:
                            divs = self.Wait.until(
                                EC.presence_of_all_elements_located(
                                    (By.CSS_SELECTOR, "h3.t")))
                        for div in divs:
                            if self.satisfy_condition(div):
                                self.process_block(div)
                                return True
                    return False
                except StaleElementReferenceException, e:
                    myprint.print_red_text( "stale retry2")
                    stale = True
                    continue

                except NoSuchElementException, e:
                    myprint.print_red_text(u"进入下一页错误,刷新:{0}".format(e))
                    self.logger.error(u"进入下一页错误,刷新:{0}".format(e))
                    return False
            break

        return False

    def jump_to_startpage(self, nums):
        for i in nums:
            # 第一页 跳转会导致滚动，无法定位到页首元素
            if int(i) <= 1:
                return
            self.go_to_next_page(i)

    def baiduSearch(self):
        # nums = [3,4,7,10]
        myprint.print_green_text(u"引擎:开始进入百度搜索")
        self.baidu_search(self.keyword)
        myprint.print_green_text(u"引擎:开始搜索标题")
        print "start jump to startpage..."
        if self.start_search_page:
            nums = self.start_search_page.split(",")
            if nums:
                self.jump_to_startpage(nums)
        print "jump to startpage finished ..."
        count = 1
        while True:
            if count == self.total_page:
                myprint.print_red_text(u"已到达搜索上限页数, 开始退出")
                if self.onlysearch == 0:
                    return False
                else:
                    return True
            myprint.print_green_text(u"引擎:开始第{page}页搜索".format(page=count))
            # sleep(5)
            ret = self.handle_page(count)
            if ret:
                return True
            myprint.print_green_text(
                u"引擎:第{page}页搜索失败!尝试进入下一页".format(page=count))
            count = count + 1
            ret = self.go_to_next_page()
            if not ret:
                return False
            myprint.print_green_text(u"引擎:成功进入下一页")
        return True

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

    def after_finish_search_task(self):
        #wait_function = [self.scroll_windows, self.random_click]
        self.main_win = self.browser.window_handles[-1]

        wait_function = [self.random_click]
        self.task_finished()
        wait_time = self.standby_time * 60 + 10 + time()
        while wait_time > time():
            myprint.print_green_text(u"引擎:等待状态,距离完成还有:{wait_time}秒".format(
                wait_time=int(wait_time - time())))
            if self.onlysearch == 0:
                if self.random_event_status == 1:
                    # nowhandle = self.browser.current_window_handle
                    if self.random_event_count < 5:
                        wait_function[random.randint(0,
                                                     len(wait_function) - 1)]()
                        self.random_event_count = self.random_event_count + 1
                    else:
                        myprint.print_green_text(u"引擎:随机事件次数已经达到上限")
            sleep(10)
        self.task_wait_finished()
        self.quit()  # 浏览器退出

    def run(self):
        # for i in range(0, 2):
        if True:
            try:
                if self.terminal_type == 2:
                    res = self.baiduSearchPhone()
                elif self.terminal_type == 1:
                    res = self.baiduSearch()
                if res:
                    self.after_finish_search_task()
                else:
                    myprint.print_red_text(u"引擎:搜索失败, 没有找到目标")
                    self.logger.error(u"搜索不到目标，任务状态改为8")
                    self.set_task_status(8)
                    self.update_search_times()
                    self.update_task_allot_impl_sub()
                    self.quit()
                return True
            except NoSuchElementException, e:
                myprint.print_red_text(u"找不到对应元素:{0}".format(e))
                self.task_failed(8)
                return False
            except TimeoutException, e:
                myprint.print_red_text(u"超时,找不到对应元素2:{0}".format(e))
                self.task_failed(8)
                return False
        myprint.print_red_text(e)
        myprint.print_red_text(u"引擎遇到错误:可能是网速过慢或者网络中断")
        self.task_failed()
        return False

    def scroll_windows(self):
        myprint.print_green_text(u"引擎:尝试滚动滑动条")
        self.switch_to_new_windows()
        if random.random() > 0.5:
            self.browser.execute_script(
                "window.scrollTo(0,document.body.scrollHeight)")
        else:
            self.browser.execute_script("window.scrollTo(0,0)")

    def random_click(self):
        if self.cm == 0:
            return
        myprint.print_green_text(u"引擎:尝试随机点击")
        self.browser.switch_to.window(self.main_win)
        # self.switch_to_new_windows()
        a_tags = self.browser.find_elements_by_css_selector("a>img")
        try:
            randa = random.choice(a_tags)
            while randa.is_displayed():
                randa.location_once_scrolled_into_view
                #快捷键操作
                    # action = ActionChains(self.browser)
                    # elem = driver.find_element_by_link_text("Gmail")
                    # action.move_to_element(randa).key_down(Keys.CONTROL).click(randa).key_up(Keys.CONTROL).perform()
                    # self.process_block(randa)
                #移动点击
                # self.move_to_next_btn(randa, 110, True)
                randa.click()
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
        # self.loadStatus = True
        print "f started"
        sleep(30)
        print "f finished"
        if self.loadstatus:
            print "timeout and refresh"
            self.q.put(0)
            self.set_task_status(10)
            self.browser.quit()
            os._exit(1)

    def quit(self):
        print("quit")
        self.browser.get("about:support")
        profiletmp = self.browser.execute_script(
            '''let currProfD = Services.dirsvc.get("ProfD", Ci.nsIFile);



               let profileDir = currProfD.path;



               return profileDir



            ''')
        if self.copy_cookie == 1:
            if os.system("XCOPY /E /Y /C " + profiletmp + "\*.* " +
                         self.origin_profile):
                print "files should be copied :/"
        self.browser.quit()
        sleep(5)
        shutil.rmtree(profiletmp, True)


def get_task(db, id):
    myprint.print_green_text(u"获取任务中")
    sql = '''select t3.* from vm_cur_task t1 INNER JOIN baiduSearchIdMap t2 on 
    t1.cur_task_id = t2.taskid LEFT JOIN baiduSearch t3 on t3.id = t2.search_id
    where t1.id = {id}  and t3.status = 1'''.format(
        id=id)
    res = db.select_sql(sql, 'DictCursor')
    if not res or len(res) == 0:
        myprint.print_green_text(u"没有获取到任务")
        return None
    myprint.print_green_text(u"获取到{length}个任务".format(length=len(res)))
    for v in res:
        v['keyword'] = v['keyword'].decode("utf8")
        v['title'] = v['title'].decode("utf8")
        v['area'] = v['area'].decode("utf8")
    return res


def init():
    myprint.print_green_text(u"程序初始化中")
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
            for t in res:
                c_rate = t['click_rate']
                cr = ClickRate(c_rate) 
                cm = cr.be_click_or_not()
        
                if t['method'] == None:
                    t['method'] = "url"
                format_data = {
                    'keyword': t['keyword'],
                    'title': t['title'],
                    'url': t['url'],
                    'method': t['method'],
                    'script_name': t['script_name'],
                    'onlysearch': t['onlysearch'],
                    'click_mode': cm

                    
                }


                myprint.print_green_text(u'''

                    开始执行任务:

                    关键词:{keyword},

                    标题:{title},

                    链接:{url},

                    是否点击:{click_mode},

                    内页脚本:{script_name}'''.format(**format_data))
                myprint.print_green_text(u"===========提交引擎初始化中===========")
                engine = ChinaUSearch(logger, db, taskid, q, pids, t, cm,
                                      is_debug_mode)
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
    main()
