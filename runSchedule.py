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
import schedule
import time
from time import gmtime, strftime
from tidalrr.workers import print_elapsed_time, tidalrrStart
from tidalrr.workers.scanQueuedArtists import scanQueuedArtists
from tidalrr.workers.scanQueuedAlbums import scanQueuedAlbums
#from tidalrr.workers.scanQueuedTracks import scanQueuedTracks
from tidalrr.workers.scanQueuedPlaylists import scanQueuedPlaylists
from tidalrr.workers.scanUserPlaylists import scanUserPlaylists
from tidalrr.database import *
from tidalrr.workers.downloadQueuedOthers import *
from tidalrr.workers.downloadQueuedTracks import *

@print_elapsed_time
def startScans():
    settings = getSettings()
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" startScans")
    tidalrrStart()
    print('tidalrrStart')
    scanQueuedArtists()
    print('Done scanning artists')
    scanQueuedAlbums()
    print('Done scanning albums')
    #scanQueuedTracks()
    #print('scanQueuedTracks')
    if settings.scanUserPlaylists:
        scanUserPlaylists()
        print('scanUserPlaylist')
    scanQueuedPlaylists()
    print('scanQueuedPlaylists')
    
def forkScans():
    # Start foo as a process
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" Starting scans")
    p = multiprocessing.Process(target=startScans)
    p.start()

    # Wait a maximum of 10 seconds for foo
    # Usage: join([timeout in seconds])
    settings = getSettings()
    hours = int(settings.scansDuration)
    seconds = hours * 60 * 60
    p.join(seconds)

    # If thread is active
    if p.is_alive():
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" Scans are running... let's kill it...")
        # Terminate foo
        p.terminate()
        # Cleanup
        p.join()

@print_elapsed_time
def startDownloads():
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" startDownloads")
    tidalrrStart()
    downloadQueuedCovers()
    scanQueuedTracks()

def forkDownloads():
    # Start foo as a process
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" Starting downloads")
    p = multiprocessing.Process(target=startDownloads)
    p.start()

    # Wait a maximum of 10 seconds for foo
    # Usage: join([timeout in seconds])
    settings = getSettings()
    hours = int(settings.downloadsDuration)
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
    settings = getSettings()
    if settings.scansDuration != 0:
        print('Scans are scheduled')
        schedule.every().day.at(str(settings.scansStartHour).zfill(2)+":00").do(forkScans)
    if settings.downloadsDuration != 0:
        print('Downloads are scheduled')
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    #startScans()
    #main()
    mainSchedule()