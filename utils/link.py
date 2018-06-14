#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : link.py
# Author            : coldplay <coldplay_gz@sina.cn>
# Date              : 06.04.2018 11:54:1522986848
# Last Modified Date: 14.06.2018 10:56:1528945010
# Last Modified By  : coldplay <coldplay_gz@sina.cn>
# coding=utf-8

import logging
import logging.config
import traceback
import os


class Link(object):
    def __init__(self, profile_path, homedir, ext_name, cookie_name,
            prefs_name='prefs.js'):
        self.ext_name = ext_name
        self.cookie_name = cookie_name
        self.profile_path = profile_path
        self.prefs_name = prefs_name
        self.homedir = homedir


    def get_task_profile_path(self, task_id):
        ppath = self.homedir+"/profile/"+str(task_id)
        return ppath


    def link(self, src_path, file_name, profile_id):
        profile_src_path = os.path.join(self.profile_path, src_path)
        sym_link = os.path.join(profile_src_path, file_name)
        dst_path = self.get_task_profile_path(profile_id)
        dst_path = os.path.join(dst_path, file_name)
        print (sym_link,dst_path)
        try:
            os.unlink(sym_link)
        except:
            pass
        try:
            os.symlink(dst_path, sym_link)
        except:
            pass

    def link_ext(self, ext_dir, profile_id):
        self.link(ext_dir, self.ext_name, profile_id)


    def link_cookie(self,cookie_dir, profile_id):
        self.link(cookie_dir, self.cookie_name, profile_id)

    def link_prefs(self,prefs_dir, profile_id):
        self.link(prefs_dir, self.prefs_name, profile_id)

if __name__ == '__main__':
    l = Link("/home/cp/.mozilla/firefox/btv8jtat.default",'/home/cp',
            'jid1-AVgCeF1zoVzMjA@jetpack.xpi',
            'cookies.sqlite')
    # l.link_ext("extensions", 1)
    l.link_cookie("", 1)
