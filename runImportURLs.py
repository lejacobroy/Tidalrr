#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   runImportURLs.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import os

from tidalrr.workers.scanURLs import *

def mainCommand():
    file_path = os.path.abspath(os.path.dirname(__file__))+'/import/urls.txt'
    startImportFile(file_path)

mainCommand()