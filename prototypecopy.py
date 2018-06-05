# -*- coding: utf-8 -*-
import os
import sys
import shutil
import random
import dbutil
import string
import datetime
import subprocess
import logging
import time
import logging.config
import urllib2
import urllib
import threading
import psutil
import Queue
import pyautogui
import ctypes
import re
from time import sleep
import os
import sys
#from ua import get_pc_ua, get_phone_ua
from ColorPrint import Color
from sys_clean import SysClean

myprint = Color()


class prototype(object):
    def __init__(self, logger,db,task_cur_id,q,pids, cm=1, is_ad=0, is_debug_mode=0):
        self.task_cur_id = task_cur_id
        self.logger = logger
        self.db = db
        self.pids = pids
        self.q = q
        self.wait_stauts = False
        self.get_information()
        self.sys_clean=SysClean(logger, pids)
        self.sys_clean.startup_check()
        # self.startup_check()
        self.total_time_mutex = threading.Lock()
        self.total_time = 0
        self.is_running = True
        self.browser = None
        self.is_debug_mode = is_debug_mode
        self.cm = cm
        self.is_ad = is_ad
        if self.is_debug_mode == 0:
            t = threading.Timer(60, self.time_counter,(q,))
            t.start()


    def time_counter(self,q):
        if q.empty():
            self.total_time_mutex.acquire()
            self.total_time = self.total_time + 1
            self.total_time_mutex.release()
            myprint.print_green_text(u"引擎:计时器增加时间, 目前时间为:{total}".format(total = self.total_time))
            myprint.print_green_text(u"引擎:任务是否运行 {is_running}".format(is_running = self.is_running))
            myprint.print_green_text(u"引擎:超时时间为:{timeout}".format(timeout= self.timeout))
            sql = "update vm_cur_task set ran_minutes = {total_time}, update_time = CURRENT_TIMESTAMP where id = {task_cur_id}".format(task_cur_id = self.task_cur_id, total_time = self.total_time)
            res = self.db.execute_sql(sql)
            # self.showpids(self.pids)
            if res < 0:
                self.logger.error("update ran_times error")
            if self.total_time > self.timeout:
                myprint.print_red_text(u"引擎:任务超时, 开始杀死引擎")
                self.sys_clean.closebroswer()
                # self.closebroswer()
                # self.close_third_windows()
                self.set_task_status(6)
                # self.update_task_allot_impl_sub()
                self.log(status=6, end_time="CURRENT_TIMESTAMP")
                self.update_profile_status()
                myprint.print_red_text(u"引擎:退出")
                os._exit(-1)
            t = threading.Timer(60, self.time_counter,(q,))
            t.start()
        else:
            myprint.print_green_text(u"引擎:计时器停止")
            os._exit(-1)



#    def get_phone_ua(self):
#        sql = "select useragent from firefox_ua where type = 2"
#        res = self.db.select_sql(sql, "DictCursor")
#        if not res or len(res) == 0:
#            return get_phone_ua(1)
#        else:
#            return res[0]["useragent"]
#
#    def get_pc_ua(self):
#        sql = "select useragent from firefox_ua where type = 1"
#        res = self.db.select_sql(sql, "DictCursor")
#        if not res or len(res) == 0:
#            return get_pc_ua(1)
#        else:
#            return res[0]["useragent"]

    def get_information(self):
        sql = "select server_id, vm_id, cur_task_id, cur_profile_id, task_group_id,user_type,terminal_type,standby_time,timeout, copy_cookie,click_mode from vm_cur_task where id = {id}".format(id = self.task_cur_id)
        #sql = "select server_id, vm_id, cur_task_id, cur_profile_id, task_group_id  from vm_cur_task where id = {id}".format(id=self.task_cur_id)
        res = self.db.select_sql(sql, 'DictCursor')
        if res is None or len(res) == 0:
            self.logger.error("can't get information")
            sys.exit()
        self.server_id = res[0]["server_id"]
        self.vm_id = res[0]["vm_id"]
        self.profile_id = res[0]["cur_profile_id"]
        self.task_id = res[0]["cur_task_id"]
        self.task_group_id = res[0]["task_group_id"]
        self.user_type = res[0]["user_type"]
        self.terminal_type = res[0]["terminal_type"]
        # sql = "select standby_time, timeout,copy_cookie from vm_task where id = {task_id}".format(task_id=self.task_id)
        # res = self.db.select_sql(sql, 'DictCursor')
        # if res is None or len(res) == 0:
        #     self.logger.error("can't get information standby_time")
        #     sys.exit()
        self.standby_time = res[0]["standby_time"]
        self.timeout = res[0]["timeout"]
        self.copy_cookie = res[0]["copy_cookie"]

    def getip(self):
        try:
            myip = self.open_url("http://ip.cha127.com/")
        except Exception, e:
            try:
                myip = self.open_url("http://www.ip138.com/ip2city.asp")
            except Exception, e:
                return "no ip!!!"
        return re.search('\d+\.\d+\.\d+\.\d+', myip).group(0)

    def open_url(self, url):
        request = urllib2.urlopen(url)
        response = request.read()
        return response

    def send_ctime(self):
        format_data = {
            'server_id': self.server_id,
            'vm_id': self.vm_id,
            'task_id': self.task_id,
            'ctime': self.total_time
        }
        url = "http://192.168.1.21/vm/ad_stat2?sid={server_id}&gid={vm_id}&tid={task_id}&c_times={ctime}".format(**format_data)
        response = self.open_url(url)
        self.logger.info("send request: {response}".format(response=response))

    def update_db_log(self):
        try:
            format_data = {
                'server_id': self.server_id,
                'vm_id': self.vm_id,
                'profile_id': self.profile_id,
                'terminal_type':self.terminal_type,
                'user_type': self.user_type
            }
            checksql = '''select create_time from vm_users where server_id = {server_id} and vm_id = {vm_id} and profile_id = {profile_id} and user_type={user_type} and terminal_type={terminal_type}'''.format(
                **format_data)
            checkret = self.db.select_sql(checksql, 'DictCursor')
            if checkret:
                if checkret[0]['create_time'] is None:
                    sql = '''update vm_users set create_time=now(),status=1 where server_id = {server_id} and vm_id = {vm_id} and profile_id = {profile_id} and user_type={user_type} and terminal_type={terminal_type}'''.format(
                        **format_data)
                    ret = self.db.execute_sql(sql)
                    if ret:
                        return True
                    else:
                        return False
                else:
                    sql = '''update vm_users set last_access_time=now(),status=1 where server_id = {server_id} and vm_id = {vm_id} and profile_id = {profile_id} and user_type={user_type} and terminal_type={terminal_type}'''.format(
                        **format_data)
                    ret = self.db.execute_sql(sql)
                    if ret:
                        return True
                    else:
                        return False
            else:
                return False
        except Exception, e:
            return False


    def success_add(self):
        try:
            format_data = {
                'server_id': self.server_id,
                'vm_id': self.vm_id,
                'terminal_type': self.terminal_type,
                'user_type': self.user_type
            }
            sql = '''update zero_schedule_list set succ_times = succ_times + 1 where time_to_sec(NOW()) between time_to_sec(start_time) and time_to_sec(end_time) and server_id = {server_id} and vm_id = {vm_id} and terminal_type = {terminal_type} and user_type ={user_type};'''.format(**format_data)
            ret = self.db.execute_sql(sql)
            if ret:
                return True
            else:
                return False
        except Exception, e:
            return False



    def task_finished(self):
        myprint.print_green_text(u"引擎:开始提交平台成功情况")
        self.is_running = False
        self.set_task_status(2)
        self.update_profile_status()
        self.log(status=2, end_time="CURRENT_TIMESTAMP")
        self.total_time_mutex.acquire()
        self.total_time = 0
        self.exit = True
        self.total_time_mutex.release()
        self.wait_stauts = True
        self.update_ran_times(True)

    def task_wait_finished(self):
        self.end_task()
        self.set_task_status(4)
        self.log(status=4, end_time="CURRENT_TIMESTAMP")
        # self.update_ran_times(True)

    def task_failed(self, status=5):
        myprint.print_green_text(u"引擎:开始提交平台失败情况")
        self.is_running = False
        self.set_task_status(5)
        self.log(status=status, end_time="CURRENT_TIMESTAMP")
        if not self.wait_stauts:
            self.update_task_allot_impl_sub()
            self.update_ran_times(False)
        self.end_task()


    # 记录函数,任务完成后记录
    def log(self, **kwargs):
        params = {}
        params.update(kwargs)
        oprcode = self.get_oprcode_bytask()
        self.log_task_timepoint(oprcode, params)
        # self.send_ctime()

    def log_task_timepoint(self, oprcode, params):
        ip = self.getip()
        sql = '''insert into vm_task_log(oprcode,'''
        keys = params.keys()
        key1 = keys[0]
        key2 = keys[1]
        values = params.values()
        value1 = values[0]
        value2 = values[1]
        sql_log = sql+"%s,%s,ip,log_time) values(%s,%s,%s,'%s', CURRENT_TIMESTAMP)"%(key1, key2, oprcode, value1,value2, ip) 
        self.logger.info(sql_log)
        ret = self.db.execute_sql(sql_log)
        if ret < 1:
            self.logger.info("sql:%s ret:%d", sql_log, ret)

    def get_oprcode_bytask(self):
        format_data = {
            "server_id": self.server_id,
            "group_id": self.vm_id,
            "task_id": self.task_id
        }
        sql_oprcode = "select oprcode from vm_oprcode where server_id={server_id} and group_id={group_id} and task_id={task_id} \
                      order by create_time desc limit 1".format(**format_data)
        res = self.db.select_sql(sql_oprcode, 'DictCursor')
        if res:
            return res[0]["oprcode"]
        return None

    def update_ran_times(self, success):
        format_data = {
            "task_group_id" : self.task_group_id,
            "task_id"       : self.task_id
        }
        sql = None
        if success:
            sql = "update vm_task_group set ran_times = ran_times + 1, allot_times = allot_times + 1, task_latest_succ_time = CURRENT_TIMESTAMP where id = {task_group_id} and task_id = {task_id}".format(**format_data)
        else:
            sql = "update vm_task_group set allot_times = allot_times + 1 where id = {task_group_id} and task_id = {task_id}".format(**format_data)

        print sql
        ret = self.db.execute_sql(sql)
        if ret < 0:
            self.logger.error("update ran times failed")

    def update_task_allot_impl(self):
        format_data = {
            "task_id": self.task_id,
            "group_id": self.task_group_id
        }
        sql = "update vm_task_allot_impl set ran_times=ran_times + 1 where id = {group_id} and task_id = {task_id} and time_to_sec(NOW()) between time_to_sec(start_time) and time_to_sec(end_time)".format(**format_data)
        ret = self.db.execute_sql(sql)
        if ret < 0:
            self.logger.error("update_task_allot_impl")

    def update_task_allot_impl_sub(self):
        format_data = {
            "task_id": self.task_id,
            "group_id": self.task_group_id
        }
        sql = '''update vm_task_allot_impl set ran_times=ran_times - 1 where id = {group_id} and task_id = {task_id} 
        and time_to_sec(NOW()) between time_to_sec(start_time) and time_to_sec(end_time) and ran_times>0'''.format(**format_data)
        ret = self.db.execute_sql(sql)
        if ret < 0:
            self.logger.error("update_task_allot_impl_sub")


    def set_task_status(self, status):
        res = None
        if status == 2:
            sql = "update vm_cur_task set status = {status}, succ_time=CURRENT_TIMESTAMP, update_time=CURRENT_TIMESTAMP, click_mode={cm} where id = {cur_task_id}".format(status = status, cur_task_id = self.task_cur_id, cm=self.cm)
        else:
            sql = "update vm_cur_task set status = {status}, update_time=CURRENT_TIMESTAMP, click_mode={cm}  where id = {cur_task_id}".format(status = status, cur_task_id = self.task_cur_id, cm=self.cm)
        res = self.db.execute_sql(sql)

        if res < 0:
            self.logger.error("update status: failed")

    def update_profile_status(self):
        format_data = {
            "status": 2,
            "server_id": self.server_id,
            "vm_id": self.vm_id,
            "task_id": self.task_id,
            "profile_id": self.profile_id
        }
        sql = "update vm_task_profile_latest set status={status} where server_id = {server_id} and vm_id = {vm_id} and task_id = {task_id} and profile_id = {profile_id}".format(**format_data)
        self.db.execute_sql(sql)

    def end_task(self):
        for i in threading.enumerate():
            if type(i) == threading._Timer:
                i.cancel()


if __name__ == "__main__":
    test_object = prototype("./baiduSearch.log.conf", 626703)
    test_object.task_finished()

