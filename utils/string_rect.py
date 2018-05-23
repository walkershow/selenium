#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : bdads.py
# Author            : coldplay <coldplay_gz@sina.cn>
# Date              : 10.05.2018 17:07:1525943254
# Last Modified Date: 10.05.2018 17:07:1525943254
# Last Modified By  : coldplay <coldplay_gz@sina.cn>
# import ImageFont

# font = ImageFont.truetype('times.ttf', 12)
# size = font.getsize('Hello world')
# print(size)

import ctypes

def GetTextDimensions(text, points, font, wp, hp):
    '''pc标题大小 wp:2.6 hp:1.5
    '''
    class SIZE(ctypes.Structure):
        _fields_ = [("cx", ctypes.c_long), ("cy", ctypes.c_long)]

    hdc = ctypes.windll.user32.GetDC(0)
    hfont = ctypes.windll.gdi32.CreateFontA(points, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, font)
    hfont_old = ctypes.windll.gdi32.SelectObject(hdc, hfont)

    size = SIZE(0, 0)
    ctypes.windll.gdi32.GetTextExtentPoint32A(hdc, text, len(text), ctypes.byref(size))

    ctypes.windll.gdi32.SelectObject(hdc, hfont_old)
    ctypes.windll.gdi32.DeleteObject(hfont)

    # return (size.cx, size.cy)
    return (int(size.cx*wp), size.cy*hp)

def GetTitleDimensions(text):
    return GetTextDimensions(text,12, "TrueType",2.6, 1.5 )


# print(GetTextDimensions("python代码:计算一个文本文件中所有大写字母,小写字母,..._百度知道", 12, "TrueType"))
