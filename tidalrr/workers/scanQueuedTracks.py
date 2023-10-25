#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   scanQueuesTracks.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''

from tidalrr.database import *
from tidalrr.settings import *
from tidalrr.tidal import *
from tidalrr.workers import *
from tidalrr.workers.scanQueuedAlbums import *

def scanQueuedTracks():
    tracks = getTidalTracks()
    if len(tracks) > 0 :
        for track in tracks:
            start_track(track)

def start_track(obj: Track):
    album = TIDAL_API.getAlbum(obj.album)
    if SETTINGS.saveCovers:
        scanCover(album)
    scanTrack(obj, album)

def scanTrack(track: Track, album=None, playlist=None):
    file = getFileById(track.id)
    if file is None:
        #try:
        stream = TIDAL_API.getStreamUrl(track.id, SETTINGS.audioQuality)
        artist = getTidalArtist(track.artist)
        album = getTidalAlbum(track.album)

        path = getTrackPath(track, stream, artist, album, playlist)

        number = 0
        if track.trackNumberOnPlaylist:
            number = track.trackNumberOnPlaylist
        else:
            number = track.trackNumber
        # check exist
        """ if isSkip(path, stream.url):
            # check if file is not already in db/linked to table file or queue
            print(str(number)+ " : " + artist.name + " - " + album.title + " - " + track.title + " (skip:already exists!)")
            return True, path """

        queue = Queue(
            type='Track',
            login=True,
            id=track.id,
            path=path,
            url=stream.url,
            encryptionKey=stream.encryptionKey
        )

        addTidalQueue(queue)
        
        print(str(number)+ " : " + artist.name + " - " + album.title + " - " + track.title)
        return True, path
        """ except Exception as e:
            print(f"DL Track[{track.title}] failed.{str(e)}")
            return False, str(e) """
    else:
        print('File Exists, skipping')