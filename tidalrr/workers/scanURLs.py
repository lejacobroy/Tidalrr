#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   workerScanURLs.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import aigpy
from tidalrr.events import *
from tidalrr.settings import *
from tidalrr.workers import *
from tidalrr.workers.scanQueuedArtists import *
from tidalrr.workers.scanQueuedAlbums import *
from tidalrr.workers.scanQueuedTracks import *
from tidalrr.workers.scanQueuedPlaylists import *

def readFile(val):
    print('Using file list: '+val)
    file1 = open(val, 'r')
    Lines = file1.readlines()
    # Strips the newline character
    for i, line in enumerate(Lines):
        print("Url #{}: {}".format(i, line.strip()))
        start(line.strip())

def start(string):
    strings = string.split(" ")
    for item in strings:
        if aigpy.string.isNull(item):
            continue

        try:
            etype, obj = TIDAL_API.getByString(item)
        except Exception as e:
            print(str(e) + " [" + item + "]")
            return

        try:
            print('start_type', etype)
            if etype == Type.Artist:
                addTidalArtist(obj)
                scanQueuedArtists()
            elif etype == Type.Track:
                addTidalTrack(obj)
                scanQueuedTracks()
            elif etype == Type.Album:
                addTidalAlbum(obj)
                scanQueuedAlbums()
            elif etype == Type.Playlist:
                addTidalPlaylist(obj)
                scanQueuedPlaylists()
            #elif etype == Type.Mix:
                #start_mix(obj)
        except Exception as e:
            print(str(e))

def startScanURLs(val):
    tidalrrStart()
    readFile(val)
