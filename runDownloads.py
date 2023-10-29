#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   runDownloads.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import multiprocessing
import schedule
import time
import functools
from time import gmtime, strftime
from tidalrr.workers import tidalrrStart
from tidalrr.workers.downloadQueuedOthers import *
from tidalrr.workers.downloadQueuedTracks import *


# This decorator can be applied to any job function to log the elapsed time of each job
def print_elapsed_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_timestamp = time.time()
        print('LOG: Running job "%s"' % func.__name__)
        result = func(*args, **kwargs)
        print('LOG: Job "%s" completed in %d seconds' % (func.__name__, time.time() - start_timestamp))
        return result

    return wrapper

@print_elapsed_time
def startDownloads():
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" startDownloads")
    tidalrrStart()
    downloadQueuedCovers()
    downloadQueuedTracks()
    
def forkDownloads():
    # Start foo as a process
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" Starting downloads")
    p = multiprocessing.Process(target=startDownloads)
    p.start()

    # Wait a maximum of 10 seconds for foo
    # Usage: join([timeout in seconds])
    hours = 6
    seconds = hours * 60 * 60
    p.join(seconds)

    # If thread is active
    if p.is_alive():
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" Downloads are running... let's kill it...")
        # Terminate foo
        p.terminate()
        # Cleanup
        p.join()

def mainSchedule():
    schedule.every().day.at("23:00").do(forkDownloads)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    #startDownloads()
    #main()
    mainSchedule()