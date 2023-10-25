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
from tidalrr.workers import tidalrrStart
from tidalrr.workers.scanQueuedArtists import scanQueuedArtists
from tidalrr.workers.scanQueuedAlbums import scanQueuedAlbums
from tidalrr.workers.scanQueuedTracks import scanQueuedTracks
from tidalrr.workers.scanQueuedPlaylists import scanQueuedPlaylists

def main():
    tidalrrStart()
    print('tidalrrStart')
    scanQueuedArtists()
    print('scanQueuedArtists')
    scanQueuedAlbums()
    print('scanQueuedAlbums')
    scanQueuedTracks()
    print('scanQueuedTracks')
    scanQueuedPlaylists()
    print('scanQueuedPlaylists')
    
main()