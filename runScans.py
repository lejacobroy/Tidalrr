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
from tidalrr.workers import tidalrrStart
from tidalrr.workers.scanQueuedArtists import scanQueuedArtists
from tidalrr.workers.scanQueuedAlbums import scanQueuedAlbums
from tidalrr.workers.scanQueuedTracks import scanQueuedTracks
from tidalrr.workers.scanQueuedPlaylists import scanQueuedPlaylists

def main():
    tidalrrStart()
    print('tidalrrStart')
    scanQueuedArtists()
    print('Done scanning artists')
    scanQueuedAlbums()
    print('Done scanning albums')
    scanQueuedTracks()
    print('scanQueuedTracks')
    scanQueuedPlaylists()
    print('scanQueuedPlaylists')
    
def startDownloads():
    # Start foo as a process
    p = multiprocessing.Process(target=main, name="downloads", args=())
    p.start()

    # Wait a maximum of 10 seconds for foo
    # Usage: join([timeout in seconds])
    hours = 6
    seconds = hours * 60 * 60
    p.join(seconds)

    # If thread is active
    if p.is_alive():
        print("download is running... let's kill it...")
        # Terminate foo
        p.terminate()
        # Cleanup
        p.join()

def mainSchedule():
    schedule.every().day.at("23:00").do(startDownloads)
    while True:
        schedule.run_pending()
        time.sleep(1)

mainSchedule()