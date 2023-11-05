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
from tidalrr.tidal import *
from tidalrr.workers import *

def scanQueuedTracks():
    tracks = getTidalTracks()
    if len(tracks) > 0 :
        for i,track in enumerate(tracks):
            if hasattr(track, 'id') and track.queued:
                if track.queued:
                    print('Scanning track '+ str(i)+'/'+str(len(tracks))+' '+track.title)
                    result = start_track(track)
                    if result:
                        track.queued = False
                        updateTidalTrack(track)

def start_track(obj: Track):
    settings = getSettings()
    if not hasattr(getTidalArtist(obj.artist), 'id'):
            # insert artist in db
            addTidalArtist(TIDAL_API.getArtist(obj.artist))
        #same for album
    if not hasattr(getTidalAlbum(obj.album), 'id'):
        # insert artist in db
        addTidalAlbum(TIDAL_API.getAlbum(obj.album))
    album = getTidalAlbum(obj.album)
    if settings.saveCovers:
        scanCover(album)
    file = getFileById(obj.id)
    queue = getTidalQueueById(obj.id)
    if file is None and queue is None:
        return scanTrack(obj, album)
    else:
        print('File Exists, skipping')
        return True

def scanTrackPath(track=Track, album=Album, playlist=Playlist):
    path = ''
    settings = getSettings()
    stream = TIDAL_API.getStreamUrl(track.id, settings.audioQuality)
    artist = getTidalArtist(track.artist)
    if artist is not None and stream is not None:
        path = getTrackPath(track, stream, artist, album, playlist)
    return stream, path

def scanTrack(track: Track, album=Album, playlist=None):
    stream, path = scanTrackPath(track, album, playlist)
    if path != '':
        queue = Queue(
            type='Track',
            login=True,
            id=track.id,
            path=path,
            url=stream.url,
            encryptionKey=stream.encryptionKey,
            urls = stream.urls
        )

        addTidalQueue(queue)
        print('Adding track to queue '+track.title)
        return True
    else:
        print('Track '+str(track.id)+' Unknown artist or url'+ str(track.artist)+' '+ track.artists)
        # maybe add the artist and re-run
        return False