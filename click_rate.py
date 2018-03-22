#!/usr/bin/env python    
#encoding: utf-8  

import pyautogui
import random
import os
import bisect

class ActionError(Exception):
    pass

class WeightedRandomGenerator(object):
    def __init__(self, weights):
        self.totals = []
        running_total = 0

        for w in weights:
            running_total += w
            self.totals.append(running_total)

    def next(self):
        rnd = random.random() * self.totals[-1]
        return bisect.bisect_right(self.totals, rnd)

    def __call__(self):
        return self.next()

class ClickRate(object):
    def __init__(self, rate):
        self.click_rate = rate
        self.non_click_rate = 100 - rate

    def be_click_or_not(self):
        '''0:click
           1:non_click
        '''
        wrg = WeightedRandomGenerator([ self.non_click_rate, self.click_rate])
        n = wrg()
        return n

if __name__ == "__main__":
    cr = ClickRate(80)
    print cr.be_click_or_not()
