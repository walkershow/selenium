#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : string_rect.py
# Author            : coldplay <coldplay_gz@sina.cn>
# Date              : 10.05.2018 17:07:1525943254
# Last Modified Date: 11.06.2018 10:52:1528685569
# Last Modified By  : coldplay <coldplay_gz@sina.cn>
# import ImageFont

# font = ImageFont.truetype('times.ttf', 12)
# size = font.getsize('Hello world')
# print(size)
import sys

if sys.platform == "win32":
    import ctypes

    def GetTextDimensions(text, points, font, wp=1, hp=1):
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
        return (int(size.cx*wp), int(size.cy*hp))

    def GetTitleDimensions(text):
        return GetTextDimensions(text,12, "TrueType",2.0, 1.2 )

else:
    import Tkinter as tk  
    import tkFont  
    
    def display_font(text, font_family, font_size, wp=1, hp=1):  
        root = tk.Tk()  
        canvas = tk.Canvas(root, width=200, height=100)  
        canvas.pack()  
        (x,y) = (5,5)  
        pttopx = lambda x:int(x * 3 // 4)  
        font_size=pttopx(font_size)  
        font = tkFont.Font(family=font_family, size=font_size)  
        w= font.measure(text)  
        h= font.metrics("linespace")  
        w = w*wp
        h = h*hp
        print "Font Family is %s, Font Size is %d pt" % (font_family,font_size)  
        print "Text Width is %s px, height is %s px" % (w,h)  
        return w*wp, h*hp
        # canvas.create_text(x,y,text=text,font=font,anchor=tk.NW)  
        # tk.mainloop()  

    def GetTitleDimensions(text):
        return (200,12)
        # return GetTextDimensions(text,12, "TrueType",1.3, 1.2 )

display_font("python代码:计算一个文本文件中所有大写字母,小写字母,..._百度知道","TrueType",12) 
# print(GetTextDimensions("python代码:计算一个文本文件中所有大写字母,小写字母,..._百度知道", 12, "TrueType"))
