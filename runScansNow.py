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
from tidalrr.workers.scanQueuedArtists import scanQueuedArtists
from tidalrr.workers.scanQueuedAlbums import scanQueuedAlbums
#from tidalrr.workers.scanQueuedTracks import scanQueuedTracks
from tidalrr.workers.scanQueuedPlaylists import scanQueuedPlaylists
from tidalrr.workers.scanUserPlaylists import scanUserPlaylists

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