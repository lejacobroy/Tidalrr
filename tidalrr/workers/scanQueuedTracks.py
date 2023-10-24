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
from tidalrr.downloadUtils import *

def scanQueuedTracks():
    tidalrrStart()
    tracks = getTidalTracks()
    for i, track in enumerate(tracks):
        start_track(Track(*track))

def start_track(obj: Track):
    album = TIDAL_API.getAlbum(obj.album)
    if SETTINGS.saveCovers:
        downloadCover(album)
    scanTrack(obj, album)

def scanTrack(track: Track, album=None, playlist=None):
    try:
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
        if isSkip(path, stream.url):
            # check if file is not already in db/linked to table file or queue
            print(str(number)+ " : " + artist.name + " - " + album.title + " - " + track.title + " (skip:already exists!)")
            return True, path

        queue = Queue(
            type='Track',
            login=True,
            id=track.id,
            path=path,
            url=stream.url,
            encryptionKey=stream.encryptionKey
        )

        addTidalQueue(queue)

        # contributors
        try:
            contributors = TIDAL_API.getTrackContributors(track.id)
        except:
            contributors = None

        # lyrics
        try:
            lyrics = TIDAL_API.getLyrics(track.id).subtitles
            if SETTINGS.lyricFile:
                lrcPath = path.rsplit(".", 1)[0] + '.lrc'
                aigpy.file.write(lrcPath, lyrics, 'w')
        except:
            lyrics = ''
        metadataArtist = getTidalArtist(album.artist)
        metadataArtists = getArtistsName(json.loads(album.artists))
        setMetaData(track, album, metadataArtist, metadataArtists, path, contributors, lyrics)
        
        print(str(number)+ " : " + artist.name + " - " + album.title + " - " + track.title)
        return True, path
    except Exception as e:
        print(f"DL Track[{track.title}] failed.{str(e)}")
        return False, str(e)

scanQueuedTracks()