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
import sys
import getopt

from tidalrr.workers.scanURLs import *

def mainCommand():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   ":f:", 
                                   ["file"])
    except getopt.GetoptError as errmsg:
        print(vars(errmsg)['msg'] + ". Use 'tidalrr -f' and a filepath.")
        return

    for opt, val in opts:
        if opt in ('-f', '--file'):
            startScanURLs(val)
            continue

mainCommand()