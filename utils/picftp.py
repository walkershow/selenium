#!/usr/bin/env python
# File              : picftp.py
# Author            : coldplay <coldplay_gz@sina.cn>
# Date              : 06.04.2018
# Last Modified Date: 06.04.2018 16:09:1523002167
# Last Modified By  : coldplay <coldplay_gz@sina.cn>
# coding=utf-8

import ftp
import time
import os
import logging
import logging.config
import traceback


class PicFTP(ftp.FTP):
    def __init__(self, addr, port, username, password, logger, server_id,
                 vm_id):
        ftp.FTP.__init__(self, addr, port, username, password, logger)
        self.server_id = server_id
        self.vm_id = vm_id

    def dir_path(self, task_id):
        cur_date = time.strftime('%Y%m%d')
        dirpath = '{0}/{1}'.format(cur_date, task_id)
        return dirpath

    def filename(self, id):
        # cur_time = time.strftime('%H%M%S')
        
        fname = '{0}_{1}_{2}'.format(self.server_id, self.vm_id, id )
        return fname

    def mkdir(self, path):
        dirs = os.path.split(path)
        for d in dirs:
            try:
                self.ftp.mkd(d)
            except:
                pass
            finally:
                self.ftp.cwd(d)
        self.ftp.cwd(self.remotedir)

    def upload_task_file(self, task_id, id, localfile):
        dirpath = self.dir_path(task_id)
        self.mkdir(dirpath)
        remote_filename = self.filename(id)
        print remote_filename
        remote_path = os.path.join(dirpath, remote_filename + ".jpg")
        self.upload_file(localfile, remote_path)


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
    ftp = PicFTP('192.168.1.53', 21, 'uppic', '123456', logger, 12, 1)
    ftp.login()
    ftp.upload_task_file(121, '/home/cp/selenium/0.py')
