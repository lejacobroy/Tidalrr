#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2020/11/08
@Author  :   Yaronzz
@Version :   3.0
@Contact :   yaronhuang@foxmail.com
@Desc    :   
'''
import sys
import getopt

from events import *
from settings import *


def mainCommand():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   "hoq:u:f:", 
                                   ["help", "url", "file", "output", "quality"])
    except getopt.GetoptError as errmsg:
        Printf.err(vars(errmsg)['msg'] + ". Use 'tidalrr -h' for usage.")
        return

    for opt, val in opts:
        if opt in ('-h', '--help'):
            Printf.usage()
            return
        if opt in ('-v', '--version'):
            Printf.logo()
            return
        if opt in ('-u', '--url'):
            use_url(val)
            continue
        if opt in ('-f', '--file'):
            Printf.info('Using file list: '+val)
            file1 = open(val, 'r')
            Lines = file1.readlines()
            count = 0
            # Strips the newline character
            for line in Lines:
                count += 1
                Printf.info("Url #{}: {}".format(count, line.strip()))
                use_url(line.strip())
            continue
        if opt in ('-o', '--output'):
            SETTINGS.downloadPath = val
            SETTINGS.save()
            continue
        if opt in ('-q', '--quality'):
            SETTINGS.audioQuality = SETTINGS.getAudioQuality(val)
            SETTINGS.save()
            continue

def use_url(url):
    if not aigpy.path.mkdirs(SETTINGS.downloadPath):
        Printf.err(LANG.select.MSG_PATH_ERR + SETTINGS.downloadPath)
        return

    if url is not None:
        if not loginByConfig():
            loginByWeb()
        Printf.info(LANG.select.SETTING_DOWNLOAD_PATH + ':' + SETTINGS.downloadPath)
        start(url)

def main():
    SETTINGS.read(getProfilePath())
    TOKEN.read(getTokenPath())
    TIDAL_API.apiKey = apiKey.getItem(SETTINGS.apiKeyIndex)
    
    if len(sys.argv) > 1:
        mainCommand()
        return
    
    #Printf.logo()
    #Printf.settings()
    
    if not apiKey.isItemValid(SETTINGS.apiKeyIndex):
        changeApiKey()
        loginByWeb()
    elif not loginByConfig():
        loginByWeb()
    
    Printf.checkVersion()


if __name__ == '__main__':
    # test()
    main()
