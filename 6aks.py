# -*- coding: utf-8 -*-
#51的W2上测试

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import argparse
import optparse
from time import sleep
import dbutil
import logging
import logging.config
import os
import random
import urllib2
import pyautogui
import urllib
import re
import math
import thread


logger = None
db = None
#vm_id = 2
#server_id = 582
db_host = "192.168.1.21"
db_user = "vm"
db_pwd = "123456"
db_name = "vm3"
db_charset = "utf8"

istest = False

class Engine(object):
    '''点击6A资讯里的360广告'''
    profile_type = -1
    profile_path = ""
    detialpage_url = []  # 存放所有资讯新闻URL
    detialpage_div = [] #存放详细页DIV
    ad_url = [] #存放广告链接
    ad_keyword = '' #广告关键字
    browser = None
    outtime = -1 #超时
    server_id = -1
    vm_id = -1
    taskid = -1

    def __init__(self, taskid):
        logger.debug(u'初始引擎')
#        if profiletype != self.profile_type:
#            self.profile_type = profiletype
#            self.change_profiles()
        self.taskid = taskid
        self.gettaskinfo()
       # self.change_profiles()

    def gettaskinfo(self):
        #server_id,vm_id,terminal_type,timeout,cur_profile_id:从profiles取得path；写入start_time,写入运行状态status:0:未运行 1:运行中 2:完成,3没输入,4待机完成,5没有窗口,6任务超时
        #更新已运行分钟数ran_minutes,
        global db
        try:
            if db == None:
                db = dbutil.DBUtil(logger, db_host, 3306, db_name, db_user, db_pwd, db_charset)
                db.create_connection()

            cur_profile_id = -1
            sql = "select server_id,vm_id,terminal_type,cur_profile_id,timeout from vm_cur_task  where id={0} ".format(self.taskid)
            res = db.select_sql(sql, 'DictCursor')
            for r in res:
                self.server_id = r['server_id']
                self.vm_id = r['vm_id']
                self.profile_type = r['terminal_type']
                cur_profile_id = r['cur_profile_id']
                self.outtime = r['timeout'] #超时
            sql = "select path from profiles where id={profileid}".format(profileid=cur_profile_id)#取得浏览器路径
            res = db.select_sql(sql)
            self.profile_path = res[0][0]
        except Exception, e:
            logger.error(u'取任务信息出错:' + str(e))
            return -1

        #从表里取得搜索内容

    def change_profiles(self): #取浏览器配置文件，用于打开浏览器时选取哪个配置文件
        mapping = {
            "0" : "",
            "1" : ".pc",
            "2" : ".wap"
        }
        self.profile_path = []
        temp_folder = os.listdir("D:\\profile") #浏览器配置文件路径，可变
        target = mapping[str(self.profile_type)]
        for f in temp_folder:
            if f.find(target) != -1:
                self.profile_path.append(os.path.join("D:\\profile\\", f))

    def initbrowser(self):
        try:
           # randnum = random.randint(0, len(self.profile_path) - 1)  # 选择随机浏览器
            print(self.profile_path)#[randnum])
            fp = webdriver.FirefoxProfile(self.profile_path) #设置浏览器配置文件位置
            fp.set_preference('permissions.default.image', 1)
            # fp = webdriver.FirefoxProfile() #设置浏览器配置文件位置
            print('select path')
            self.browser = webdriver.Firefox(fp)
            print('set firefox')
            #self.browser.set_page_load_timeout(20)  # 设置页面超时时间
            #print('set timeout')
            return 0
        except TimeoutException, e:
            logger.error(u'初始浏览器超时:' + str(e.message))
            return -1
        except Exception, e:
            logger.error(u'初始浏览器失败:' + str(e.message))
            return 0

    def switch_to_new_windows(self):
        sleep(1)
        try:
            windows = self.browser.window_handles
            self.browser.switch_to.window(windows[-1])
        except Exception, e:
            logger.error(u'客户广告页动作错误:' + str(e.message))

    def GoToIndexPage(self,url):
        logger.debug(u"打开首页")
        try:
            print (url)
            self.browser.get(url)
            return 0
        except TimeoutException, e:
            return 0
        except Exception, e:
            logger.error(u'打开首页错误:' + str(e.message))
            return -1

    def OpenListUrl(self,select):
        logger.debug(u"打开列表页")
        try:
            sleep(5)
            title = self.browser.find_element_by_css_selector(select)
            url = title.get_attribute('href')
            #title.click()
            if url != "":
                self.browser.get(url)
            #self.switch_to_new_windows()
            return 0
        except Exception , e:
            logger.error(u'打开列表页错误:' + str(e.message))
            return -1

    def GetDetailUrl(self,select,div):#取得详细页URL(加多一个div做为另一种情况，点不到select部分就点div部分)
        logger.debug(u'取得详细页URL，存入数组')
        print(u'取得详细面URL:' + select)
        try:
            self.browser.switch_to.default_content()
            print(self.browser.title)
            news_as = WebDriverWait(self.browser, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, select)))
            #'li.smalive_list>a'
            #news_as = self.browser.find_elements_by_xpath("//li[@class='smalive_list']/a")
            #news_as = self.browser.find_elements_by_css_selector(select)
            #news_as = self.browser.find_elements_by_xpath("//div[5]/div[2]/div[1]/div[2]/div[2]/ul/li[@class='smalive_list']/a")
            self.detialpage_url = []
            print(str(len(news_as)))
            self.detialpage_url = news_as
            self.browser.switch_to.default_content()
            self.browser.switch_to.default_content()
            self.detialpage_div =  WebDriverWait(self.browser, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, div)))
         #   for a in news_as:
         #       tt = a.get_attribute("href")
         #       print(tt)
         #       self.detialpage_url.append(tt)
            return 0
        except Exception , e:
            logger.error(u'取得详细页URL错误:' + str(e.message))
            return -1
       
    def OpenDetialPage(self):#随机打开一条详细页
        logger.debug(u"随机打开一条详细页")
        urlcount = len(self.detialpage_url)
        print(urlcount)
        if urlcount <= 0:
            print(u'详细页URL数量为0')
            return -1

        try:
            openurl = random.choice(self.detialpage_url)
            print('1')
            #self.browser.get(openurl)
            #openurl.click()
            try:
                url = openurl.get_attribute("href")
                self.browser.get(url)
                print(url)
            except Exception, e:
                openurl = random.choice(self.detialpage_div)
                openurl.click()
                #self.process_block(openurl)
                #print(openurl.text)
                print('click')
            sleep(5)
            print('2')
            #self.switch_to_new_windows()
            #self.Process_360SearchPage()
            return 0
        except TimeoutException, e:
            logger.debug(u'打开详细页超时:' + str(e.message))
            return -1
        except Exception, e:
            logger.error(u'打开详细页错误:' + str(e.message))
            return -1

    def GetAllAdUrl(self,iframeindex,iframename,adhref): #取得所有广告URL，存放 ad_url[]里
        #self.browser.get("http://sh.qihoo.com/pc/detail?url=http%3A%2F%2Fzm.news.so.com%2F77f32c2cccd72a7e5828f4cd43137222&check=101b0a19caf065f7&uid=f4b297612057a4978740f68e11cb8c11&sign=360_79aabe15")
        logger.debug(u"取详细页中所有360广告URL")
        print(u"取详细页中所有360广告URL")
        try:
            lenifname = len(iframename)
            leniframe = len(iframeindex)
            selector_as = []
            self.ad_url = []
            ifindex = 0
            # 有N层就建几个iframeN循环,复制下面三句和一句self.browser.switch_to.parent_frame(),比如6a是有两层，就有两个循环；那个宝宝网站就只有一个循环
            #iframes0 = self.browser.find_elements_by_css_selector('iframe')
            #for iframe0 in iframes0:
            #    self.browser.switch_to_frame(iframe0)
            iframes1 = self.browser.find_elements_by_css_selector('iframe')
            for iframe1 in iframes1:
                ifindex += 1
                bfound = False
                if leniframe == 0 and lenifname == 0:
                    bfound = True
                for index in iframeindex:
                    if ifindex == index:
                        bfound = True
                        break
                if bfound == False:#找不到索引号时，找类名
                    try:
                        ifname = iframe1.get_attribute("name")
                        for name in iframename:
                            if name == ifname:
                                bfound = True;
                                break
                    except Exception,e:
                        pass
                if bfound == False:
                    continue
                self.browser.switch_to_frame(iframe1)
                ads = self.browser.find_elements_by_css_selector('a')
                for ad in ads:
                    tt = ad.get_attribute('href')
                    if tt != None:
                        if tt.find(adhref) != -1: #这是360广告标识
                            self.ad_url.append(tt)
                self.browser.switch_to.parent_frame()#每个for对应一句这个
                #self.browser.switch_to.parent_frame()
            if len(self.ad_url) <= 0:
                print(u'详细页中,找不到广告内容')
            return 0
        except Exception, e:
            logger.error(u'取详细页所有广告URL错误:' + str(e.message))
            return -1


    def OpenAdPage(self): #随机打开一条广告
        logger.debug(u"随机打开一条广告")
        urlcount = len(self.ad_url)
        if urlcount <= 0:
            return -1
        try:
            openurl = random.choice(self.ad_url)
            self.browser.get(openurl)
            #sleep(6)
            #self.switch_to_new_windows()
            return 0
        except TimeoutException, e:
            logger.debug(u"打开一条广告超时:" + str(e.message))
            return -1
        except Exception, e:
            logger.error(u'打开一条广告错误:' + str(e.message))
            return -1

    def Process_360SearchPage(self):#360搜索页中的动作
        logger.debug(u"360搜索页中的运作")
        #一分钟内的事情：从上到下移动滚动条
        #这里的方法是，把页面高度分为60段，每秒从每段距离里随机移动距离，直到这段距离完成后进行下一段的移动，可变
        try:
            pageheight = self.browser.execute_script('''return document.body.scrollHeight''')
            moveh = 0
            nowh = 0
            for j in range(60):
                endtime = 1000 #即10秒
                moveh = (pageheight/60)*(j+1) #应该移动到的距离
                ymove = moveh - nowh #可移动的距离
                while endtime > 0:
                    i = random.randint(1,endtime) #0.1到10秒里随机
                    if i < 10:
                        i = 10
                    ranmove = random.randint(0,ymove) #随机移动距离，但不超过可移动距离
                    nowh = nowh + ranmove
                    ymove = ymove - ranmove
                    if ymove <= 0:
                        ymove = 0
                    js = "var q=document.documentElement.scrollTop={ran}".format(ran=nowh)
                    self.browser.execute_script(js)
                    s = i*0.001
                    sleep(s)
                    endtime = endtime-i
            return 0
        except TimeoutException, e:
            logger.debug(u'360搜索页操作超时:' + str(e.message))
            return -1
        except Exception, e:
            logger.error(u'360搜索页操作错误:' + str(e.message))
            return -1

    def Open360ClientAdPage(self,select):#打开客户广告页面
        logger.debug(u"打开客户广告页面")
        #ul#e_idea_pp>li>a
        #self.browser.get('https://www.so.com/s?src=lm&ls=sm2170640&lmsid=5bd864db947ac867&lm_extend=ctype:4&q=%E6%96%B0%E4%B8%9C%E6%96%B9%E9%9B%85%E6%80%9D%E7%8F%AD')
        try:
            ads = self.browser.find_elements_by_css_selector(select) #360广告详细页地址，可变
            ad = random.choice(ads)
            print('1')
            #chain = ActionChains(self.browser)
            #chain.move_to_element(ad).perform()
            self.browser.execute_script("arguments[0].scrollIntoView();", ad)
            print('2')
            scrolltop = self.browser.execute_script('return document.body.scrollTop')
            js = "var q=document.documentElement.scrollTop="+str(scrolltop+50)
            self.browser.execute_script(js)
            print('3')
            ad.click()
            print('4')
            self.switch_to_new_windows()
            print('5')
            self.browser.maximize_window()#最大化浏览器窗口
            return 0
        except TimeoutException, e:
            logger.debug(u'打开客户广告页超时:' + str(e.message))
            return -1
        except Exception, e:
            logger.error(u'打开客户广告页错误:' + str(e.message))
            return -1

        return 0

    def Process_360adPage(self): #360客户广告内动作
        logger.debug(u"360客户广告页内的动作")
        #self.browser.get('http://www.koolearn.com/ke/ielts/?a_id=ff8080813c28dbf2013c28dbf24e0000&kid=9bd24eaccd9f446a8684e975ef25bd9b&utm_source=360&utm_medium=pcss&utm_campaign=%E9%9B%85%E6%80%9D-%E5%93%81%E7%89%8C%E8%AF%8D&utm_content=%E6%96%B0%E4%B8%9C%E6%96%B9%E9%9B%85%E6%80%9D&utm_term=%E6%96%B0%E4%B8%9C%E6%96%B9%E9%9B%85%E6%80%9D%E5%AD%A6%E6%A0%A1&ctx=&basePath=http%3A%2F%2Fun.koolearn.com%3A80%2F')
        #sleep(2)
        try:
            js = "var q=document.documentElement.scrollTop=10000"#滚动条移动最底下
            self.browser.execute_script(js)
            self.RandomMoveMouse()
            return 0
        except TimeoutException, e:
            logger.debug(u'客户广告页动作超时:' + str(e.message))
            return -1
        except Exception, e:
            logger.error(u'客户广告页动作错误:' + str(e.message))
            return -1

    def RandomMoveMouse(self):  # 让鼠标朝目录曲线移动，这个随机移动是可调整的，看实际情况变动
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
        width, height = pyautogui.size()  # 得到屏幕坐标
        r = 250
        s = random.randint(2, 5)
        o_x = width / s
        o_y = height / s
        pi = 3.1415926

        nowtime = 0
        while nowtime < 120: #2分钟内进行运动
            try:
                html =  self.browser.find_elements_by_css_selector('html')
            except Exception, e: #浏览器已被关闭
                return;
            i = 0
            for angle in range(rangex, rangey, 5):  # 光标画圆
                r = random.randint(100,250)
                X = o_x + r * math.sin(angle * pi / 180)
                Y = o_y + r * math.cos(angle * pi / 180)
                if i == 0:
                    pyautogui.moveTo(X, Y, duration=1)  # duration移动到XY花费的时间
                    nowtime = nowtime + 1
                else:
                    pyautogui.moveTo(X, Y, duration=0.1)
                    nowtime = nowtime + 0.1
                i = i + 1
       # pyautogui.moveTo(190, 0)
       # pyautogui.moveTo(190, height, duration=5)


    def Quit(self): #关浏览器
            try:
                self.browser.quit()
             #   windows = self.browser.window_handles
             #   for win in windows:
             #       self.browser.switch_to_window(win)
             #       self.browser.close()
            except Exception, e:
                logger.error(u'关闭浏览器错误:' + str(e.message))
          #  self.browser.close()
            logger.debug(u"关闭浏览器")


    def so6a(self,select,select1,select2):
        sleep(2)
        self.browser.find_element_by_xpath(select).send_keys(select1)
        sleep(1)
        self.browser.find_element_by_xpath(select2).send_keys(Keys.ENTER)
        sleep(5)
        return 0

    def goTo17173(self,select,select1):
        try:
            titles = WebDriverWait(self.browser, 10).until(EC.presence_of_all_elements_located(( By.TAG_NAME, select )))
        except Exception, e:
            print("Can't Found The h3 tags in baidu")
        for title in titles:                                                                   
            if title.text.find(select1) != -1:
                title.find_element_by_tag_name("a").click()
        sleep(8)
        self.switch_to_new_windows()
        sleep(5)
        #print self.now_handle
        return 0
      
    def goTo58(self,select,select1,select2):
        sleep(5)
        self.browser.find_element_by_xpath(select).send_keys(select1)
        sleep(3)
        self.browser.find_element_by_xpath(select2).send_keys(Keys.ENTER)
        sleep(5)
        return 0

    def SetStart_Time_Status(self):
        global db
        if db == None:
            db = dbutil.DBUtil(logger, db_host, 3306, db_name, db_user, db_pwd, db_charset)
            db.create_connection()
        try:
            sql = "update vm_cur_task set start_time=CURRENT_TIMESTAMP,status=1 where id={0}".format(self.taskid)
            res = db.execute_sql(sql)
            return res
        except Exception,e:
            logger.error(u'设置开始标识出错:' + str(e))
            return -1

    def SetFinishRunStatus(self):
        global db
        try:
            if db == None:
                db = dbutil.DBUtil(logger, db_host, 3306, db_name, db_user, db_pwd, db_charset)
                db.create_connection()
            sql = "update vm_cur_task set status = 4,succ_time=CURRENT_TIMESTAMP,update_time=CURRENT_TIMESTAMP where id={0} ".format(self.taskid)  # 任务完成时设置状态
            res = db.execute_sql(sql)
            return res
        except Exception, e:
            logger.error(u'设置完成标识出错:' + str(e))
            return -1

    def run(self):
        ret = self.SetStart_Time_Status()#设置开始运行状态标识和启动时间
        if ret < 0:
            return -1
            #self.wait_vpndial_ok() #等待VPN拨号成功，不用拨号时注销
        ret = self.initbrowser()
        if ret != 0:
            self.Quit()
            return -1
        ret = self.GoToIndexPage("http://www.baidu.com")#('http://www.mvqcs.cn/index.html') #打开首页("http://www.6a.com")
        if ret != 0:
            self.Quit()
            return -1

        ret = self.so6a("//*[@id=\"kw\"]","6a",'''//*[@id="su"]''')  #百度1717
        if ret != 0:
            self.Quit()
            return -1

        self.Quit()
        ret = self.SetFinishRunStatus()#设置完成状态标识
        if ret < 0:
            return -1
        logger.debug("任务完成")
        return 0

         #   self.task_finished_set_isdial() #任务完成，要求拨号; 不要拨号时注销




def main():
    global db
    global logger
    global vm_id
    global server_id
    global  db_namez

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s%(filename)s[line:%(lineno)d]%(levelname)s %(message)s',
                        datefmt='%a,%d %b %Y %H:%M:%S',  # a是星期几单词 b为日期 b为几月份单词
                        filename='myapp.log', filemode='w'  # w为重写 a为追加写入--
                        )
    try:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')  # -12s表示间隔多少
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
    except Exception, e:
        pass
    logging.config.fileConfig("log_conf/6aks.log.conf")
    logger = logging.getLogger("example02")

    logger.debug(u'启动程序')
    print(u"启动程序")

    parser = argparse.ArgumentParser(description='set task id')
#    parser.add_argument('-browsertype', type=int, default=1, help="1为pc,2为wap") #运行时：python news360ad.py --browsertype=2
#    parser.add_argument('-vmid', type=int, default=2, help='vmid')
#    parser.add_argument('-serverid', type=int, default=582, help='serverid')
#    parser.add_argument('-dbname', type=str, default='vm2', help='dbname')
    parser.add_argument('-t',type=int,default=0,help='task id')
    args = parser.parse_args()
#    browsertype = args.browsertype
#    vmid = args.vmid
#    server_id = args.serverid
#    db_name = args.dbname
#    print(browsertype)
#    print(vm_id)
#    print(server_id)
#    print(db_name)
    taskid = args.t
    if istest == True:
        taskid=3228997
    engine = Engine(taskid)
    engine.run()
    if db != None:
        db.close_connection()
    logger.debug(u'退出程序')
    print(u"退出程序")

if __name__ == "__main__":
    main()
