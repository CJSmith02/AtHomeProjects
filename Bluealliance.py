# -*- coding: utf-8 -*-
"""
Created on Sun May  3 19:58:19 2020

@author: 1750801058
"""
import requests

TBA_KEY = 'lAKLrKkaL8NSLlrcleXo1ucKphqqPkVGQDOnQ564bmEP1IbYNBUOqCSGz0X5tmoe'
BASE = 'https://www.thebluealliance.com/api/v3'


def get_tba(path):
    return requests.get(BASE + path, params = {'X-TBA-Auth-Key' : TBA_KEY})

