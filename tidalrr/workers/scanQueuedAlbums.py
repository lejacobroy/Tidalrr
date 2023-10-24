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
    tidalrrStart()
    albums = getTidalAlbums()
    for i, album in enumerate(albums):
        start_album(Album(*album))

def start_album(obj: Album):
    tracks = TIDAL_API.getItems(obj.id, Type.Album)
    for i in tracks:
        addTidalTrack(i)
    if SETTINGS.saveAlbumInfo:
        downloadAlbumInfo(obj, tracks)
    if SETTINGS.saveCovers and obj.cover is not None:
        downloadCover(obj)

def downloadCover(album):
    if album is None:
        return
    path = getAlbumPath(album) + '/cover.jpg'
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


def downloadAlbumInfo(album:Album, tracks: [Track]):
    if album is None:
        return

    path = getAlbumPath(album)
    aigpy.path.mkdirs(path)

    path += '/AlbumInfo.txt'
    infos = ""
    infos += "[ID]          %s\n" % (str(album.id))
    infos += "[Title]       %s\n" % (str(album.title))
    infos += "[Artists]     %s\n" % (getArtistsName(album.artists))
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
    
scanQueuedAlbums()