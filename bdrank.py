#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
import optparse
import threading
import os
import urllib2
from os.path import basename
from urlparse import urlsplit
from time import sleep
from time import time
import shutil
import random
import re
import sys
import dbutil
import importlib
import logging
import logging.config
from prototype import prototype
from ColorPrint import Color
from pypinyin import pinyin, lazy_pinyin, Style 
import wubi
import urllib

logger = None
db = None
cur_task_id = None
db_host = "192.168.1.21"
db_name = "vm2"
db_user = "vm"
db_pwd = "123456"
db_charset = "utf8"
myprint = Color()

import random
from pypinyin import pinyin, lazy_pinyin, Style

class PinYinWord(object):
    def __init__(self, string, wubi_status = False):
        self.is_Chinese = self.check_contain_chinese(string)
        if self.is_Chinese:
            if wubi_status == False:
                pinyinList = lazy_pinyin(string)
            else:
                pinyinList = wubi.get(string,'cw').split(" ")
            self.string = ""
            for w in pinyinList:
                
                self.string += w[0:random.randint(0, len(w) - 1)]
        else:
            self.string = string
        self.replace_string = string

    def check_contain_chinese(self, check_str):
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

class PinYin(object):
    def __init__(self, string):
        self.split_word(string)
        self.finish_list = []
        if random.random() > 0.5:
            fucked = True
        else:
            fucked = False
        for word in self.split_list:
            if fucked == True:
                self.finish_list.append(PinYinWord(word))
            else:
                self.finish_list.append(PinYinWord(word, True))
    
    def getList(self):
        return self.finish_list

    def split_word(self, string):
        self.split_list = []
        temp_word = ""
        is_Chinese = False
        is_first_word = True
        for s in string:
            if is_first_word:
                temp_word += s
                is_first_word = False
                is_Chinese = self.check_is_chinese(s)
                continue
            status = self.check_is_chinese(s)
            if status != is_Chinese:
                self.split_list.append(temp_word)
                temp_word = s
                is_Chinese = status
            else:
                temp_word += s
        self.split_list.append(temp_word)

    def check_is_chinese(self, check_char):
        if u'\u4e00' <= check_char <= u'\u9fff':
            return True

    def check_contain_chinese(self, check_str):
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

class ChinaUSearch(prototype):
    db_host = "192.168.1.21"
    db_name = "vm2"
    db_user = "vm"
    db_pwd = "123456"
    db_charset = "utf8"

    resolution = [
        (1600, 900),
        (1366, 768),
        (1920, 1080),
        (1440, 900),
        (1680, 1050),
        (1920, 1200),
        (2560, 1600),
    ]


    def __init__(self, taskid, task):
        myprint.print_green_text(u"引擎:初始化本体")
        super(ChinaUSearch, self).__init__("./log_conf/{script_name}.log.conf".format(script_name = task["script_name"]), taskid)
        self.script_name = task["script_name"]
        self.title = task["title"]
        self.keyword = task["keyword"]
        self.url = task["url"]
        self.id = task["id"]
        self.random_event_status = task['random_event_status']
        self.total_page = task['total_page']
        self.terminal_type = task["terminal_type"] # 终端
        self.profile_type = task["terminal_type"]
        self.random_event_count = 0
        self.module = importlib.import_module("script.{script_name}".format(script_name = self.script_name))
        self.db = dbutil.DBUtil(self.logger, self.db_host, 3306, self.db_name, self.db_user, self.db_pwd, self.db_charset)
        myprint.print_green_text(u"引擎:初始化本体成功")
        myprint.print_green_text(u"引擎:初始化浏览器")
        self.webdriver_config()
        # browser init
        # width, height = self.get_resolution_pc()
        # mobile_emulation = {
        #     "deviceMetrics": { "width": width, "height": height, "pixelRatio": 1.0 }
        # }
        # if self.terminal_type == 2:
        #     mobile_emulation['userAgent'] = self.get_phone_ua()
        # else:
        #     mobile_emulation['userAgent'] = self.get_pc_ua()
        # myprint.print_green_text(u"引擎:获取到桌面分辨率为:{width}*{height}".format(width = width, height = height))
        # myprint.print_green_text(u"引擎:获取到UA为:{ua}".format(ua = mobile_emulation["userAgent"]))
        # option = webdriver.ChromeOptions()
        # option.add_experimental_option("mobileEmulation", mobile_emulation)
        # self.browser = webdriver.Chrome(chrome_options=option)
        self.Wait = WebDriverWait(self.browser, 10)
        myprint.print_green_text(u"引擎:初始化浏览器成功")

    def webdriver_config(self):
        try:
            mapping = {
                "1" : ".pc",
                "2" : ".wap"
            }
            self.profile_path = []
            temp_folder = os.listdir("D:\\profile")
            target = mapping[str(self.profile_type)]
            for f in temp_folder:
                if f.find(target) != -1:
                    self.profile_path.append(os.path.join("D:\\profile\\", f))
            caps = DesiredCapabilities().FIREFOX
            caps["marionette"] = False
            profile = random.sample(self.profile_path,1)
            sql = "select path from profiles where id = {profile_id}".format(profile_id = self.profile_id)
            res = self.db.select_sql(sql, 'DictCursor')
            if res is None or len(res) == 0:
                self.logger.error("can't get information profile_path")
            self.profile_path = res[0]['path']
            fp = webdriver.FirefoxProfile(self.profile_path)
            self.browser = webdriver.Firefox(fp, capabilities=caps)
        except Exception,e:
            print "the webdriver config failed,{0}".format(e)
            sys.exit() 



    def get_resolution_pc(self):
        return self.resolution[random.randint(0, len(self.resolution) - 1)]

    def baidu_search(self, keyword):
        self.browser.get('''http://www.baidu.com''')
        sleep(1)
        input_block = self.browser.find_element_by_xpath('''//*[@id="kw"]''')
        keyword_fuck = PinYin(keyword)
        myfuck_list = keyword_fuck.getList()
        for word in myfuck_list:
            if word.is_Chinese == True:
                for w in word.string:
                    input_block.send_keys(w)
                    sleep(random.uniform(0.2, 1.5))
                sleep(1)
                script_str = '''function replace_last_str(origin_str, target_str, replace_str){var index = origin_str.lastIndexOf(target_str);return origin_str.substr(0, index) + replace_str + origin_str.substr(index + target_str.length);}value = document.getElementById("kw").value;document.getElementById("kw").value = replace_last_str(value, "{origin}", "{replace_str}")'''
                script_str = script_str.replace("{origin}", word.string).replace("{replace_str}", word.replace_string)
                self.browser.execute_script(script_str)
                #self.browser.execute_script(u'''document.getElementById("kw").value = document.getElementById("kw").value.replace("{origin}", "{replace_str}")'''.format(origin = word.string, replace_str = word.replace_string))
            else:
                for w in word.string:
                    input_block.send_keys(w)
                    sleep(random.uniform(0.2, 1.5))
        input_block.send_keys(Keys.ENTER)
        sleep(2)

    def baidu_search_phone(self, keyword):
        self.browser.get('''http://m.baidu.com''')
        sleep(1)
        input_block = self.Wait.until(
            EC.presence_of_element_located((By.ID, "index-kw")))
        keyword_fuck = PinYin(keyword)
        myfuck_list = keyword_fuck.getList()
        for word in myfuck_list:
            if word.is_Chinese == True:
                for w in word.string:
                    input_block.send_keys(w)
                    sleep(random.uniform(0.2, 1.5))
                sleep(1)
                script_str = '''function replace_last_str(origin_str, target_str, replace_str){var index = origin_str.lastIndexOf(target_str);return origin_str.substr(0, index) + replace_str + origin_str.substr(index + target_str.length);}value = document.getElementById("index-kw").value;document.getElementById("index-kw").value = replace_last_str(value, "{origin}", "{replace_str}")'''
                script_str = script_str.replace("{origin}", word.string).replace("{replace_str}", word.replace_string)
                self.browser.execute_script(script_str)
                #self.browser.execute_script(u'''document.getElementById("kw").value = document.getElementById("kw").value.replace("{origin}", "{replace_str}")'''.format(origin = word.string, replace_str = word.replace_string))
            else:
                for w in word.string:
                    input_block.send_keys(w)
                    sleep(random.uniform(0.2, 1.5))
        # for w in keyword:
        #     input_block.send_keys(w)
        #     sleep(random.uniform(0.2, 1.5))
        input_block.send_keys(Keys.ENTER)
        sleep(2)

    def satisfy_condition(self, block):
        if block.text.find(self.title) != -1 and block.text.find(self.url) != -1:
            return True
        else:
            return False

    def satisfy_condition_phone(self, block):
        try:
            h3_tag = block.find_element_by_tag_name("h3")
            a_tag = block.find_element_by_tag_name("a")
            link = a_tag.get_attribute("href")
            # dirty code for fucker network, like shit
            while True:
                try:
                    r = urllib2.Request(link)
                    f = urllib2.urlopen(r, data=None, timeout=4)
                    result =  f.read()
                    break
                except Exception,e:
                    myprint.print_red_text(e)
            re_result = re.search(r'window.location.replace\("(.*)"\)', result)
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
        except Exception, e:
            myprint.print_red_text(e)
            return False

    def process_block(self, title):
        self.browser.execute_script("arguments[0].click()", title.find_element_by_tag_name("a"))
        

    def go_to_next_page(self):
        a_list = self.browser.find_elements_by_css_selector("a.n")
        for a in a_list:
            if a.text == u"下一页>":
                a.click()
                sleep(3)
                return True
        return False
    
    def go_to_next_page_phone(self):
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        sleep(4)
        page_source = self.browser.page_source
        next_page_link = None
        if page_source.find("class=\"new-nextpage\"") != -1:
            next_page_link = self.browser.find_element_by_css_selector("a.new-nextpage")
        elif page_source.find("class=\"new-nextpage-only\"") != -1:
            next_page_link = self.browser.find_element_by_css_selector("a.new-nextpage-only")
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
        self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        while True:
            if count == self.total_page:
                myprint.print_red_text(u"已到达搜索上限页数, 开始退出")
                return False
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            sleep(4) 
            myprint.print_green_text(u"引擎:开始第{page}页搜索".format(page = count))
            divs = self.Wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.c-container"))
            )
            for div in divs:
                if self.satisfy_condition_phone(div):
                    self.process_block(div)
                    return True
            count = count + 1
            myprint.print_green_text(u"引擎:第{page}页搜索失败!尝试进入下一页".format(page = count))
            ret = self.go_to_next_page_phone()

            if ret == False:
                return False
            myprint.print_green_text(u"引擎:成功进入下一页")

    def baiduSearch(self):
        myprint.print_green_text(u"引擎:开始进入百度搜索")
        self.baidu_search(self.keyword)
        myprint.print_green_text(u"引擎:开始搜索标题")
        count = 1
        while True:
            if count == self.total_page:
                myprint.print_red_text(u"已到达搜索上限页数, 开始退出")
                return False
            myprint.print_green_text(u"引擎:开始第{page}页搜索".format(page = count))
            divs = self.Wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.c-container"))
            )
            for div in divs:
                if self.satisfy_condition(div):
                    self.process_block(div)
                    return True
            count = count + 1
            myprint.print_green_text(u"引擎:第{page}页搜索失败!尝试进入下一页".format(page = count))
            ret = self.go_to_next_page()
            if ret == False:
                return False
            myprint.print_green_text(u"引擎:成功进入下一页")

    def switch_to_new_windows(self):
        myprint.print_green_text(u"引擎:切换标签")
        sleep(1)
        windows = self.browser.window_handles
        self.browser.switch_to.window(windows[-1])

    def __del__(self):
        self.browser.quit()

    def update_search_times(self):
        myprint.print_green_text(u"引擎:添加成功搜索次数")
        sql = "update baiduSearch set had_search_times = had_search_times + 1 where id = {id}".format(id = self.id)
        ret = self.db.execute_sql(sql)
        if ret < 0:
            myprint.print_red_text(u"引擎:添加成功搜索次数失败, 可能是网络原因导致!")
            self.logger.error("update sql failed : {sql}".format(sql = sql))

    def check_contain_chinese(self, check_str):
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    # 随机点击
    def random_click(self):
        myprint.print_red_text(u"测试专用=======================引擎:随机点击=======================")
        try:
            self.switch_to_new_windows()
            a_tags = self.browser.find_elements_by_css_selector("a>img")
            randa = random.choice(a_tags)
            randa.location_once_scrolled_into_view
            randa.click()
        except Exception, e:
            pass
        myprint.print_red_text(u"测试专用=======================引擎:随机点击结束=======================")

    def after_finish_search_task(self):
        wait_function = [
            self.scroll_windows,
            self.random_click
        ]

        self.update_search_times()
        self.task_finished()
        wait_time = self.standby_time * 60 + 10 + time()
        while wait_time > time():
            myprint.print_green_text(u"引擎:等待状态,距离完成还有:{wait_time}秒".format(wait_time = int(wait_time - time())))
            if self.random_event_status == 1:
                if self.random_event_count < 5:
                    wait_function[random.randint(0, len(wait_function) - 1)]()
                    self.random_event_count = self.random_event_count + 1
                else:
                    myprint.print_green_text(u"引擎:随机事件次数已经达到上限")
            sleep(10)
        self.task_wait_finished()
        self.quit() #浏览器退出


    def run(self):

        try:
            if self.terminal_type == 2:
                res = self.baiduSearchPhone()
            else:
                res = self.baiduSearch()
            if res == True:
                myprint.print_green_text(u"引擎:成功进入目标页面, 接下来交给子脚本")
                self.engine = self.module.Engine(self.browser)
                self.engine.run()
                myprint.print_green_text(u"引擎:子脚本完成")
                self.switch_to_new_windows()
                self.random_click()
                self.after_finish_search_task()
            else:
                myprint.print_red_text(u"引擎:搜索失败, 没有找到目标")
                self.task_finished()
                self.task_wait_finished()
            return True
        except Exception, e:
            self.quit()
            myprint.print_red_text(e)
            myprint.print_red_text(u"引擎遇到错误:可能是网速过慢或者网络中断")
            self.logger.error("=======================error:{0}======================".format(e))
            sleep(10)
            self.task_failed()
            return False
    
    def scroll_windows(self):
        myprint.print_green_text(u"引擎:尝试滚动滑动条")
        self.switch_to_new_windows()
        if random.random() > 0.5:
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        else:
            self.browser.execute_script("window.scrollTo(0,0)")

    def random_click(self):
        myprint.print_green_text(u"引擎:尝试随机点击")        
        self.switch_to_new_windows()
        a_tags = self.browser.find_elements_by_css_selector("a>img")
        try:
            randa = random.choice(a_tags)
            randa.location_once_scrolled_into_view
            randa.click()
        except Exception, e:
            pass

    def quit(self):
        print("quit")
        self.browser.quit()

def get_task(db, id):
    myprint.print_green_text(u"获取任务中")
    sql = "select t3.* from vm_cur_task t1 INNER JOIN baiduSearchIdMap t2 on t1.cur_task_id = t2.taskid LEFT JOIN baiduSearch t3 on t3.id = t2.search_id where t1.id = {id} and t3.had_search_times < t3.search_times and t3.status = 1".format(id = id)
    res = db.select_sql(sql, 'DictCursor')
    if not res or len(res) == 0:
        myprint.print_green_text(u"没有获取到任务")
        return None
    myprint.print_green_text(u"获取到{length}个任务".format(length = len(res)))
    for v in res:
        v['keyword'] = v['keyword'].decode("utf8")
        v['title'] = v['title'].decode("utf8")
        v['area'] = v['area'].decode("utf8")
    return res
    
def send_message_to_vpn(cur_taskid, area):
    myprint.print_green_text(u"获取本机ServerID当中")
    sql = "select server_id from vm_cur_task where id = {id}".format(id = cur_taskid)
    res = db.select_sql(sql, 'DictCursor')
    if not res or len(res) == 0:
        myprint.print_red_text(u"获取本机ServeerID失败,放弃拨号")
        return False
    serverid = res[0]['server_id']

    myprint.print_green_text(u"通知vpn拨号, 拨号地区为:{area}".format(area = area))
    sql = "update vm_isdial_baidu set isdial = 1 where serverid = {serverid}".format(serverid = serverid)
    res = db.execute_sql(sql)
    if res < 0:
        myprint.print_red_text(u"通知vpn拨号失败,放弃拨号")
        return False

    while True:
        sql = "select isdial from vm_isdial_baidu where serverid = {serverid}".format(serverid = serverid)
        res = db.select_sql(sql, 'DictCursor')
        if not res or len(res) == 0:
            myprint.print_red_text(u"等待vpn拨号失败, 暂时10秒")
            sleep(10)
            continue
        if res[0]['isdial'] == 0:
            break
        myprint.print_green_text(u"等待vpn拨号, 拨号地区为:{area}".format(area = area))
        sleep(10)
    myprint.print_green_text(u"拨号成功")
    return True

def init():
    myprint.print_green_text(u"程序初始化中")
    global logger
    global db
    parser = optparse.OptionParser()
    parser.add_option("-l", "--log_file", dest="log_file", default="./baiduSearch.log.conf")
    parser.add_option("-t", "--task_id", dest="task_id")
    (options, args) = parser.parse_args()
    logging.config.fileConfig(options.log_file)
    logger = logging.getLogger("mylogger")
    db = dbutil.DBUtil(logger, db_host, 3306, db_name, db_user, db_pwd, db_charset)
    myprint.print_green_text(u"程序初始化完成, 获取到任务id:{id}".format(id = options.task_id))
    return options.task_id

def run():
    global logger

def main():
    task_id = init()
    res = get_task(db, task_id)
    #send_message_to_vpn(task_id, res[0]['area'])
    for t in res:
        try:
            format_data = {
                'keyword'   : t['keyword'],
                'title'     : t['title'],
                'url'       : t['url'],
                'script_name': t['script_name']
            }
            myprint.print_green_text(u'''
    开始执行任务:
    关键词:{keyword},
    标题:{title},
    链接:{url},
    内页脚本:{script_name}'''.format(**format_data))
            myprint.print_green_text(u"===========提交引擎初始化中===========")
            engine = ChinaUSearch(task_id, t)
            engine.run()
        except Exception:
            pass

if __name__ == "__main__":
    #myprint.print_green_text("hello")
    main()
