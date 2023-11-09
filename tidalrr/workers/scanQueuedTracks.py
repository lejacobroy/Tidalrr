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

import logging

logger = logging.getLogger(__name__)

def scanQueuedTracks():
    try:
        tracks = getTidalTracks()
        if len(tracks) > 0:
            for i, track in enumerate(tracks):
                try:
                    if hasattr(track, 'id') and track.queued:
                        if track.queued:
                            logger.info('Scanning track %s/%s %s', str(i), str(len(tracks)), track.title)
                            result = start_track(track)
                            if result:
                                track.queued = False
                                updateTidalTrack(track)
                except Exception as e:
                    logger.error("Error scanning track: %s", e)
    except Exception as e:
        logger.error("Error getting tracks: %s", e)

def start_track(obj: Track):
    try:
        settings = getSettings()
        try:
            if not hasattr(getTidalArtist(obj.artist), 'id'):
                # insert artist in db
                addTidalArtist(TIDAL_API.getArtist(obj.artist))
        except Exception as e:
            logger.error("Error adding artist: %s", e)
            
        try:    
            #same for album
            if not hasattr(getTidalAlbum(obj.album), 'id'):
                # insert artist in db
                addTidalAlbum(TIDAL_API.getAlbum(obj.album))
        except Exception as e:
            logger.error("Error adding album: %s", e)

        try:
            album = getTidalAlbum(obj.album)
            if settings.saveCovers:
                scanCover(album)
        except Exception as e:
            logger.error("Error getting album: %s", e)

        try:
            file = getFileById(obj.id)
            queue = getTidalQueueById(obj.id)
            if file is None and queue is None:
                return scanTrack(obj, album)
            else:
                logger.info('File exists, skipping')
                return True
        except Exception as e:
            logger.error("Error scanning track: %s", e)
    except Exception as e:
        logger.error("Error in scan queued tracks: %s", e)

def scanTrackPath(track=Track, album=Album, playlist=Playlist):
    path = ''
    try:
        settings = getSettings()
    except Exception as e:
        logger.error("Error getting settings: %s", e)

    try:
        stream = TIDAL_API.getStreamUrl(track.id, settings.audioQuality) 
    except Exception as e:
        logger.error("Error getting stream URL: %s", e)

    try:
        artist = getTidalArtist(track.artist)
        if artist is None:
            try:
                artist = TIDAL_API.getArtist(track.artist)
                addTidalArtist(artist)
            except Exception as e:
                logger.error("Error getting artist: %s", e)
    except Exception as e:
        logger.error("Error getting tidal artist: %s", e)

    try:
        albumArtist = getTidalArtist(album.artist)
        if albumArtist is None:
            try:
                albumArtist = TIDAL_API.getArtist(album.artist)
                addTidalArtist(albumArtist)
            except Exception as e:
                logger.error("Error getting album artist: %s", e)
    except Exception as e:
        logger.error("Error getting tidal album artist: %s", e)

    if artist is not None and stream is not None:
        try:
            path = getTrackPath(track, stream, artist, album, playlist)
        except Exception as e:
            logger.error("Error getting track path: %s", e)

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