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
from tidalrr.tidal import *
from tidalrr.workers import *

def readFile(val):
    print('Using file list: '+val)
    file1 = open(val, 'r')
    Lines = file1.readlines()
    # Strips the newline character
    for i, line in enumerate(Lines):
        print("Url #{}: {}".format(i, line.strip()))
        start(line.strip())
    print("Done import URLs from file.")

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
            # add files in queued state, to download them later
            if etype == Type.Artist:
                dbArtist = getTidalArtist(obj.id)
                if dbArtist is None:
                    obj.queued = True
                    addTidalArtist(obj)
                    print('Added artist to DB:', obj.name)
                    #scanQueuedArtists()
            elif etype == Type.Album:
                dbAlbum = getTidalAlbum(obj.id)
                if dbAlbum is None:
                    obj.queued = True
                    addTidalAlbum(obj)
                    print('Added album to DB:', obj.title)
                    #scanQueuedAlbums()
            elif etype == Type.Track:
                dbTrack = getTidalTrack(obj.id)
                if dbTrack is None:
                    obj.queued = True
                    addTidalTrack(obj)
                    print('addTidalTrack')
                    #scanQueuedTracks()
            elif etype == Type.Playlist:
                dbPlaylist = getTidalPlaylist(obj.uuid)
                if dbPlaylist is None:
                    obj.queued = True
                    addTidalPlaylist(obj)
                    print('Added playlist to DB:', obj.title)
                #scanQueuedPlaylists()
            #elif etype == Type.Mix:
                #start_mix(obj)
        except Exception as e:
            print(str(e))

def startImportFile(val):
    tidalrrStart()
    readFile(val)
