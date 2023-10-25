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

from tidalrr.database import *
from tidalrr.settings import *
from tidalrr.tidal import *
from tidalrr.workers import *

def scanQueuedAlbums():
    albums = getTidalAlbums()
    if len(albums) > 0 :
        for album in albums:
            if hasattr(album, 'id'):
                start_album(album)

def start_album(obj: Album):
    tracks = TIDAL_API.getItems(obj.id, Type.Album)
    for i in tracks:
        addTidalTrack(i)
    if SETTINGS.saveAlbumInfo:
        writeAlbumInfo(obj, tracks)
    if SETTINGS.saveCovers and obj.cover is not None:
        scanCover(obj)

def scanCover(album):
    cover = getFileById(album.id)
    if cover is None:
        if album is None:
            return
        path = getAlbumPath(album) 
        if path is not None:
            path = path + '/cover.jpg'
            url = TIDAL_API.getCoverUrl(album.cover)

            queue = Queue(
                type='Cover',
                login=False,
                id=album.id,
                path=path,
                url=url,
                encryptionKey=''
            )

            addTidalQueue(queue)
            #aigpy.net.downloadFile(url, path)

def writeAlbumInfo(album:Album, tracks: [Track]):
    if album is None:
        return

    path = getAlbumPath(album)
    if path is not None:
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
