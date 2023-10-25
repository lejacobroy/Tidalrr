#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   app.py
@Time    :   2023/10/25
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import subprocess
import sys

def main():
    subprocess.Popen([sys.executable, "runWebServer.py"])
    subprocess.Popen([sys.executable, "runImportURLs.py"])
    subprocess.Popen([sys.executable, "runScans.py"])
    subprocess.Popen([sys.executable, "runDownloads.py"])

main()