#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   scanQueuesAlbums.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
from os.path import exists
from tidalrr.database import *
from tidalrr.tidal import *
from tidalrr.workers import *
from tidalrr.workers.scanQueuedTracks import scanQueuedTracks

import logging

logger = logging.getLogger(__name__) 

def scanQueuedAlbums():
    albums = getTidalAlbums()
    if len(albums) > 0:
        for i, album in enumerate(albums):
            try:
                if hasattr(album, 'id') and album.queued:
                    print('Scanning album / ', str(i), str(len(albums)), album.title)
                    start_album(album)
                    album.queued = False
                    updateTidalAlbum(album)
            except Exception as e:
                print("Error scanning album: ", e)

def start_album(obj: Album):
    try:
        tracks = TIDAL_API.getItems(obj.id, Type.Album)
        settings = getSettings()
        if obj.queued:
            if settings.saveAlbumInfo:
                writeAlbumInfo(obj, tracks)
            if settings.saveCovers and obj.cover is not None:
                scanCover(obj)
        for i, track in enumerate(tracks):
            existing = getTidalTrack(track.id)
            if existing is None:
                try:
                    if not hasattr(getTidalArtist(track.artist), 'id'):
                        # insert artist in db
                        addTidalArtist(TIDAL_API.getArtist(track.artist))
                    # insert artist in db
                    addTidalAlbum(TIDAL_API.getAlbum(track.album))
                    print('Adding track %d/%d to DB: ', i, len(tracks), track.title)
                    if obj.queued:
                        track.queued = True
                    addTidalTrack(track)
                    scanQueuedTracks()
                except Exception as e:
                    print("Error adding track: ", e)
    except Exception as e:
        print("Error scanning album: ", e)

def writeAlbumInfo(album:Album, tracks: [Track]):
    if album is None:
        return

    path = getAlbumPath(album)
    if path is not None and not exists(path+'/AlbumInfo.txt'):
        aigpy.path.mkdirs(path)

        path += '/AlbumInfo.txt'
        infos = ""
        infos += "[ID]          \n" % (str(album.id))
        infos += "[Title]       \n" % (str(album.title))
        infos += "[Artists]     \n" % (str(album.artists))
        infos += "[ReleaseDate] \n" % (str(album.releaseDate))
        infos += "[SongNum]     \n" % (str(album.numberOfTracks))
        infos += "[Duration]    \n" % (str(album.duration))
        infos += '\n'

        for index in range(0, album.numberOfVolumes):
            volumeNumber = index + 1
            infos += f"===========CD {volumeNumber}=============\n"
            for item in tracks:
                if item.volumeNumber != volumeNumber:
                    continue
                infos += '{:<8}'.format("[%d]" % item.trackNumber)
                infos += "\n" % item.title
        aigpy.file.write(path, infos, "w+")
