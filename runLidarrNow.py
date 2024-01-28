#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   runScans.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''

import multiprocessing
from time import gmtime, strftime
from tidalrr.database import *
from tidalrr.workers import print_elapsed_time, tidalrrStart
from tidalrr.workers.syncLidarr import syncLidarr

@print_elapsed_time
def startLidarrSync():
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" startLidarrSync")
    tidalrrStart()
    print('tidalrrStart')
    syncLidarr()
    
    
def forkScans():
    # Start foo as a process
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" Starting scans")
    p = multiprocessing.Process(target=startLidarrSync)
    p.start()

    p.join()

    # If thread is active
    if p.is_alive():
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" Scans are running... let's kill it...")
        # Terminate foo
        p.terminate()
        # Cleanup
        p.join()

if __name__ == '__main__':
    forkScans()
    #main()
    #mainSchedule()