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
        for i,track in enumerate(tracks):
            if hasattr(track, 'id') and track.queued:
                print('Scanning track '+ str(i)+'/'+str(len(tracks))+' '+track.title)
                start_track(track)

def start_track(obj: Track):
    album = getTidalAlbum(obj.album)
    if SETTINGS.saveCovers:
        scanCover(album)
    file = getFileById(obj.id)
    queue = getTidalQueueById(obj.id)
    if file is None and queue is None:
        scanTrack(obj, album)
    else:
        print('File Exists, skipping')

def scanTrack(track: Track, album=Album, playlist=None):
    stream = TIDAL_API.getStreamUrl(track.id, SETTINGS.audioQuality)
    artist = getTidalArtist(track.artist)
    if artist is not None:
        path = getTrackPath(track, stream, artist, album, playlist)

        queue = Queue(
            type='Track',
            login=True,
            id=track.id,
            path=path,
            url=stream.url,
            encryptionKey=stream.encryptionKey
        )

        addTidalQueue(queue)
        print('Adding track to queue '+track.title)
    else:
        print('Track '+str(track.id)+' Unknown artist '+ str(track.artist)+' '+ track.artists)
        # maybe add the artist and re-run