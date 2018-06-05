#!/usr/bin/env python    
#encoding: utf-8  

import random
import wubi
from pypinyin import pinyin, lazy_pinyin, Style
from time import sleep

class InputMode(object):
    def __init__(self, browser):
        self.browser = browser

    def input_pinyin(self,kw,keyword,kwid):
        for word in keyword:
            for w in lazy_pinyin(word)[0]:
                kw.send_keys(w)
                sleep(random.uniform(0.2, 1.5))
            js = ''' function replace_last_str(origin_str, target_str, replace_str){
                        var index = origin_str.lastIndexOf(target_str);
                        return origin_str.substr(0, index) + replace_str + origin_str.substr(index + target_str.length);
                    }
                    value = document.getElementById("{kwid}").value;
                    document.getElementById("{kwid}").value = replace_last_str(value, "{origin}", "{replace_str}")
                '''
            js = js.replace("{origin}", lazy_pinyin(word)[0]).replace("{replace_str}", word).replace("{kwid}",kwid)
            self.browser.execute_script(js)

    def input_wubi(self,kw,keyword,kwid):
        for word in keyword:
            for w in wubi.get(word,'cw'):
                kw.send_keys(w)
                sleep(random.uniform(0.2, 1.5))
            js = ''' function replace_last_str(origin_str, target_str, replace_str){
                        var index = origin_str.lastIndexOf(target_str);
                        return origin_str.substr(0, index) + replace_str + origin_str.substr(index + target_str.length);
                    }
                    value = document.getElementById("{kwid}").value;
                    document.getElementById("{kwid}").value = replace_last_str(value, "{origin}", "{replace_str}")
                '''
            js = js.replace("{origin}",  wubi.get(word, 'cw')).replace("{replace_str}", word).replace("{kwid}",kwid)
            self.browser.execute_script(js)

    def input_paste(self, kw, keyword, kwid):
        for word in keyword:
                # kw.send_keys(word)
            sleep(random.uniform(0.2, 1.5))
            js = ''' function replace_last_str(origin_str, target_str, replace_str){
                        return origin_str + replace_str;
                    }
                    value = document.getElementById("{kwid}").value;
                    document.getElementById("{kwid}").value = replace_last_str(value, "{origin}", "{replace_str}")
                '''
            js = js.replace("{origin}", word).replace("{replace_str}", word).replace("{kwid}",kwid)
            self.browser.execute_script(js)
        
    def input(self, input_block, keyword, kwid, mode=0, brand=True):
        if brand:
            # self.input_paste(input_block, keyword, kwid)
            # return 
            mode = random.randint(0, 2)
            if mode == 0:
                self.input_pinyin(input_block, keyword, kwid)
            elif mode == 1:
                self.input_wubi(input_block, keyword, kwid)
            else:
                self.input_paste(input_block, keyword, kwid)
    
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

