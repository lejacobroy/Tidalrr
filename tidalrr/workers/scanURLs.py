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
from tidalrr.tidal import TIDAL_API, Type
from tidalrr.database.tracks import updateTidalTrack, getTidalTrack, addTidalTrack
from tidalrr.database.albums import getTidalAlbum, addTidalAlbum, updateTidalAlbum
from tidalrr.database.artists import addTidalArtist, getTidalArtist, updateTidalArtist
from tidalrr.database.playlists import updateTidalPlaylist, getTidalPlaylist, addTidalPlaylist
from tidalrr.workers import tidalrrStart

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
            # add files in monitored state, to download them later
            if etype == Type.Artist:
                dbArtist = getTidalArtist(obj.id)
                if dbArtist is None:
                    obj.monitored = True
                    addTidalArtist(obj)
                    print('Added artist to DB:', obj.name)
                    #scanQueuedArtists()
                else:
                    dbArtist.monitored = True
                    updateTidalArtist(dbArtist)
                    print('Monitored artist in DB:', obj.name)
                    #scanQueuedArtists()
            elif etype == Type.Album:
                dbAlbum = getTidalAlbum(obj.id)
                if dbAlbum is None:
                    obj.monitored = True
                    addTidalAlbum(obj)
                    print('Added album to DB:', obj.title)
                    #scanQueuedAlbums()
                else:
                    dbAlbum.monitored = True
                    updateTidalAlbum(dbAlbum)
                    print('Monitored album in DB:', obj.title)
                    #scanQueuedAlbums()
            elif etype == Type.Track:
                dbTrack = getTidalTrack(obj.id)
                if dbTrack is None:
                    obj.queued = True
                    addTidalTrack(obj)
                    print('Added track to DB:', obj.title)
                    #scanQueuedTracks()
                else:
                    dbTrack.queued = True
                    updateTidalTrack(dbTrack)
                    print('Queued track in DB:', obj.title)
                    #scanQueuedTracks()
            elif etype == Type.Playlist:
                dbPlaylist = getTidalPlaylist(obj.uuid)
                if dbPlaylist is None:
                    obj.monitored = True
                    addTidalPlaylist(obj)
                    print('Added playlist to DB:', obj.title)
                else:
                    dbPlaylist.monitored = True
                    updateTidalPlaylist(dbPlaylist)
                    print('Monitored playlist in DB:', obj.title)
                #scanQueuedPlaylists()
            #elif etype == Type.Mix:
                #start_mix(obj)
        except Exception as e:
            print(str(e))

def startImportFile(val):
    tidalrrStart()
    readFile(val)

def startImportUrl(val):
    tidalrrStart()
    print("Url #{}: {}".format(1, val.strip()))
    start(val.strip())