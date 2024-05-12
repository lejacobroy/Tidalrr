#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   runWebServer.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''

from tidalrr.tidal import waitForAuth

if __name__ == '__main__':
    print('run waitForAuth')
    waitForAuth()