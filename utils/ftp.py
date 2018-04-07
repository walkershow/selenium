#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ftp.py
# Author            : coldplay <coldplay_gz@sina.cn>
# Date              : 06.04.2018 11:54:1522986848
# Last Modified Date: 06.04.2018 15:41:1523000509
# Last Modified By  : coldplay <coldplay_gz@sina.cn>
# coding=utf-8

import ftplib
import logging
import logging.config
import traceback
import os


class FTP(object):
    def __init__(self, addr, port, username, password, logger):
        self.addr = addr
        self.port = port
        self.username = username
        self.password = password
        self.ftp = ftplib.FTP()
        self.logger = logger

    #     self.ftp      = ftplib.FTP()

    def login(self, remotedir='/'):
        try:
            self.remotedir = remotedir
            self.ftp.set_pasv(True)  #模式：被动模式
            self.ftp.connect(self.addr, self.port)  #连接：地址端口
            self.ftp.login(self.username, self.password)  #登录：用户密码
            self.logger.info("---------------------------------------------")
            self.logger.info("连接已完成：" + self.ftp.getwelcome())
        except Exception, e:
            traceback.print_exc()
            self.logger.info("连接或登录失败")
            sys.exit()  #返回一个 SystemExit异常 （退出程序）

        try:
            self.ftp.cwd(remotedir)  #变更工作目录
        except (Exception):
            self.logger.info('切换目录失败')
            sys.exit()  #返回一个 SystemExit异常 （退出程序）

    #对比文件大小
    def is_same_size(self, localfile, remotefile):
        try:
            remotefile_size = self.ftp.size(remotefile)  #远程文件的大小
        except:
            remotefile_size = -1

        try:
            localfile_size = os.path.getsize(localfile)  #本地文件的大小
        except:
            localfile_size = -1
        #print('lo:%d  re:%d' %(localfile_size, remotefile_size),)

        if remotefile_size == localfile_size:  #对比文件大小
            return 1
        else:
            return 0

    #上传文件函数
    def upload_file(self, localfile, remotefile):
        if not os.path.isfile(localfile):  #如果文件不存在
            print localfile
            return
        if self.is_same_size(localfile, remotefile):  #本地与远程文件大小一样的话（文件存在）
            self.logger.info('文件已存在: %s' % localfile)
            return
        file_handler = open(localfile, 'rb')  #打开本地要上传的文件
        self.ftp.storbinary('STOR %s' % remotefile, file_handler)  #上传本地文件
        file_handler.close()  #关闭打开的文件
        # self.logger.info('文件已传送: %s' % localfile)

    #创建子目录并执行上面的 上传文件upload_file函数
    def upload_files(self, localdir='./', remotedir='./'):
        if not os.path.isdir(localdir):  #目录是否存在
            return
        localnames = os.listdir(localdir)  #获取目录中的文件及子目录的列表
        self.ftp.cwd(remotedir)  #变更工作目录

        #循环目录下的文件与子目录
        for item in localnames:
            src = os.path.join(localdir, item)  #连接字符串
            if os.path.isdir(src):  #目录是否存在
                try:
                    self.ftp.mkd(item)  #创建目录
                except:
                    self.logger.info('目录已存在: %s' % item)
                self.upload_files(src, item)
            else:
                self.upload_file(src, item)  #上传文件（upload_file函数）
        self.ftp.cwd('..')  #变更工作目录

    def __del__(self):
        print "close ftp"
        self.ftp.close()

    #记录日志函数
    def log(msg):
        datenow = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        self.logstr = '%s : %s \n' % (datenow, msg)
        #print(self.logger.infostr)
        self.logfile.write(self.logstr)


def get_default_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # console logger
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(process)d] [%(module)s::%(funcName)s::%(lineno)d] [%(levelname)s]: %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


if __name__ == '__main__':
    logger = get_default_logger()
    ftp = FTP('192.168.1.53', 21, 'uppic', '123456', logger)
    ftp.login()
    ftp.upload_file('/home/cp/selenium/0.py', '0.py')
#     self.ftp.upload_files(, rootdir_remote)   #upload_files函数 （以上函数从这里开始）
