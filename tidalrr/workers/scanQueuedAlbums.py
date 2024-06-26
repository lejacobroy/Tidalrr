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
import aigpy
from os.path import exists
from tidalrr.model import Track, Album, Track
from tidalrr.tidal import TIDAL_API, Type
from tidalrr.database import getSettings
from tidalrr.database.tracks import getTidalTrack, addTidalTrack
from tidalrr.database.albums import addTidalAlbum, getMonitoredTidalAlbums, updateTidalAlbum
from tidalrr.database.artists import addTidalArtist, getTidalArtist
from tidalrr.workers import scanCover, getAlbumPath
import logging

logger = logging.getLogger(__name__) 

def scanQueuedAlbums():
    albums = getMonitoredTidalAlbums()
    if len(albums) > 0:
        for i, album in enumerate(albums):
            try:
                if hasattr(album, 'id'):
                    print('Scanning album ', str(i), ' / ', str(len(albums)), album.title)
                    start_album(album)
                    #album.monitored = False
                    #updateTidalAlbum(album)
            except Exception as e:
                print("Error scanning album: ", e)
                if "Album" in str(e) and "not found" in str(e):
                    album.monitored = False
                    updateTidalAlbum(album)

def start_album(obj: Album):
    try:
        tracks = TIDAL_API.getItems(obj.id, Type.Album)
        settings = getSettings()
        if obj.monitored:
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
                    print('Adding track '+str(i)+ '/'+str(len(tracks))+' to DB: '+track.title)
                    if obj.monitored:
                        # album is monitored, we will queue this track too
                        track.queued = True
                    addTidalTrack(track)
                    #scanQueuedTracks()
                except Exception as e:
                    print("Error adding track: ", str(e))
    except Exception as e:
        print("Error scanning album: ", str(e))

def writeAlbumInfo(album:Album, tracks: list[Track]):
    if album is None:
        return

    path = getAlbumPath(album)
    if path is not None and not exists(path+'/AlbumInfo.txt'):
        aigpy.path.mkdirs(path)

        path += '/AlbumInfo.txt'
        infos = ""
        infos += "[ID]          %s\n" % (str(album.id))
        infos += "[Title]       %s\n" % (str(album.title))
        infos += "[Artists]     %s\n" % (str(album.artists))
        infos += "[ReleaseDate] %s\n" % (str(album.releaseDate))
        infos += "[SongNum]     %s\n" % (str(album.numberOfTracks))
        infos += "[Duration]    %s\n" % (str(album.duration))
        infos += '\n'

        for index in range(0, album.numberOfVolumes):
            volumeNumber = index + 1
            infos += f"===========CD {volumeNumber}=============\n"
            for item in tracks:
                if item.volumeNumber != volumeNumber:
                    continue
                infos += '{:<8}'.format("[%d]" % item.trackNumber)
                infos += "%s\n" % item.title
        aigpy.file.write(path, infos, "w+")
