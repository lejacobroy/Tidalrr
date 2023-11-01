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

def scanQueuedAlbums():
    albums = getTidalAlbums()
    if len(albums) > 0 :
        for i,album in enumerate(albums):
            if hasattr(album, 'id'):
                if album.queued:
                    print('Scanning album '+ str(i)+'/'+str(len(albums))+' '+album.title)
                    start_album(album)
                    album.queued = False
                    updateTidalAlbum(album)

def start_album(obj: Album):
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
            print('Adding track to DB '+ str(i)+'/'+str(len(tracks))+' '+track.title)
            addTidalTrack(track)
            if obj.queued:
                track.queued = True
                scanQueuedTracks()

def writeAlbumInfo(album:Album, tracks: [Track]):
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
