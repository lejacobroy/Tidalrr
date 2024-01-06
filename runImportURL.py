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
import sys

from tidalrr.workers.scanURLs import *

if __name__ == '__main__':
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Importing URL: {url}")
        startImportUrl(url)
    else:
        print("Error: URL argument missing")
        print("Usage: python runImportURL.py <url>")



