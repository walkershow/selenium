#!/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from ColorPrint import Color
from time import sleep
import random

class Script:
    def __init__(self,driver,logger):
        self.browser = driver
        self.Wait = WebDriverWait(self.browser, 30)
        self.logger = logger

    def find_element_css_list(self,seletor):
        try:
            elems = self.Wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR,seletor))
            )
            return elems
        except Exception,e:
            print "查找元素超时"
            self.logger.error("{0},seletor:{1}".format(e, seletor))
            return

    def find_element_tag_list(self,seletor):
        try:
            elems = self.Wait.until(
                EC.presence_of_all_elements_located((By.TAG_NAME,seletor))
            )
            return elems
        except Exception,e:
            print "查找元素超时"
            self.logger.error("{0},seletor:{1}".format(e, seletor))
            return

    def find_elem(self,type,seletor,parent=None):
        if parent == None:
            parent = self.browser
        try:
            if type == "id":
                elem = parent.find_element_by_id(seletor)
            elif type == "name":
                elem = parent.find_element_by_name(seletor)
            elif type == "class":
                elem = parent.find_element_by_class_name(seletor)
            elif type == "tag":
                elem = parent.find_element_by_tag_name(seletor)
            elif type == "linktext":
                elem = parent.find_element_by_link_text(seletor)
            elif type == "partial":
                elem = parent.find_elements_by_partial_link_text(seletor)
            elif type == "xpath":
                elem = parent.find_element_by_xpath(seletor)
            elif type == "css":
                elem = parent.find_element_by_css_selector(seletor)
            else:
                print "错误的查询元素方式"
            return elem
        except Exception,e:
            self.logger.error("{0},seletor:{1}".format(e,seletor))
            return

    def switch_to_new_windows(self,winlist=None):
        if winlist == None:
            currentwindow = self.browser.current_window_handle
            windows = self.browser.window_handles
            for current_window in windows:
                if current_window != currentwindow:
                    self.browser.switch_to.window(current_window)
        else:
            windows = self.browser.window_handles
            if len(windows) != len(winlist):
                ret = [i for i in windows if i not in winlist]
                self.browser.switch_to.window(ret[0])

    def random_scroll(self):
        js = "return document.body.scrollHeight"
        height = self.browser.execute_script(js)
        rannum = random.sample(range(0, height), random.randint(1,3))
        for i in range(len(rannum)):
            if i == 0:
                for j in range(0, rannum[i])[::50]:
                    js = """var q=document.documentElement.scrollTop={0}""".format(j)
                    self.browser.execute_script(js)
                    sleep(0.1)
            else:
                if rannum[i - 1] < rannum[i]:
                    step = 50
                    if rannum[i] - rannum[i - 1] < 50:
                        step = 10
                    for j in range(rannum[i - 1], rannum[i])[::step]:
                        js = """var q=document.documentElement.scrollTop={0}""".format(j)
                        self.browser.execute_script(js)
                        sleep(0.1)
                else:
                    step = -50
                    if rannum[i - 1] - rannum[i] < 50:
                        step = -10
                    for j in range(rannum[i], rannum[i - 1])[::step]:
                        js = """var q=document.documentElement.scrollTop={0}""".format(j)
                        self.browser.execute_script(js)
                        sleep(0.1)



