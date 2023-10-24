#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   workerStart.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''

from tidalrr.events import *
from tidalrr.settings import *
from tidalrr.tidal import *

def tidalrrStart():
    #createTables()
    SETTINGS.read()
    TOKEN.read()
    TIDAL_API.apiKey = getItem(SETTINGS.apiKeyIndex)
    
    #Printf.logo()
    #Printf.settings()
    if not aigpy.path.mkdirs(SETTINGS.downloadPath):
        print(SETTINGS.downloadPath)
        return

    if not isItemValid(SETTINGS.apiKeyIndex):
        changeApiKey()
        loginByWeb()
    elif not loginByConfig():
        loginByWeb()