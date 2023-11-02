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
from multiprocessing import Process
from runWebServer import *
from runScans import *
from runDownloads import *

def main():
    print("Starting tidalrr app", flush=True)
    processes = []

    process1 = Process(target=webServer(False))
    process2 = Process(target=mainScansSchedule)
    process3 = Process(target=mainDownloadsSchedule)

    processes.extend([process1, process2, process3])

    for process in processes:
        process.start()

    for process in processes:
        process.join()

if __name__ == '__main__':
    main()