#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   download.py
@Time    :   2020/11/08
@Author  :   Yaronzz
@Version :   1.0
@Contact :   yaronhuang@foxmail.com
@Desc    :   
'''
""" import aigpy
import logging

from tidalrr.paths import *
from tidalrr.decryption import *
from tidalrr.tidal import *
from tidalrr.workers import * """

""" def downloadCover(album):
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
    aigpy.file.write(path, infos, "w+") """

""" def getDownloadTrackFilename(track: Track, playlist: Playlist):
    stream = TIDAL_API.getStreamUrl(track.id, SETTINGS.audioQuality)
    path = getTrackPath(track, stream, None, playlist, 'filename')
    return path
 """



""" def downloadTracks(tracks, album: Album = None, playlist : Playlist=None):
    print('downloadTracks')
    def __getAlbum__(item: Track):
        album = TIDAL_API.getAlbum(item.album.id)
        if SETTINGS.saveCovers and not SETTINGS.usePlaylistFolder:
            downloadCover(album)
            #print('downloadCover')
        return album
    paths = []

    for index, item in enumerate(tracks):
        itemAlbum = album
        if itemAlbum is None:
            itemAlbum = __getAlbum__(item)
            item.trackNumberOnPlaylist = index + 1
        paths.append(downloadTrack(item, itemAlbum, playlist)[1])

    return paths """

""" def downloadPlaylistInfos(tracks, album: Album = None, playlist : Playlist=None):
    def __getAlbum__(item: Track):
        album = TIDAL_API.getAlbum(item.album.id)
        if SETTINGS.saveCovers and not SETTINGS.usePlaylistFolder:
            downloadCover(album)
        return album
    
    for index, item in enumerate(tracks):
        itemAlbum = album
        if itemAlbum is None:
            itemAlbum = __getAlbum__(item)
            item.trackNumberOnPlaylist = index + 1
        downloadTrack(item, itemAlbum, playlist) """
