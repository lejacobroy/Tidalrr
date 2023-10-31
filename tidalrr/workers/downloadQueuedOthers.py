#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   downloadQueudOthers.py
@Time    :   2023/10/25
@Author  :   JAcob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import aigpy

from tidalrr.paths import *
from tidalrr.decryption import *
from tidalrr.tidal import *
from tidalrr.workers import *

def downloadQueuedCovers():
    covers = getTidalQueues('Cover')
    for i,cover in enumerate(covers):
        file = getFileById(cover.id)
        if file is None:
            album = getTidalAlbum(cover.id)
            # check exisitng path
            if not exists(cover.path):
                aigpy.net.downloadFile(cover.url, cover.path)
                print('Downloading album cover '+str(i)+'/'+str(len(covers))+' '+album.title)
            file = File(
                description=album.title,
                type='Cover',
                id=cover.id,
                path=cover.path
            )
            addFiles(file)
        delTidalQueue(cover.path)

""" def getDownloadTrackFilename(track: Track, playlist: Playlist):
    stream = TIDAL_API.getStreamUrl(track.id, settings.audioQuality)
    path = getTrackPath(track, stream, None, playlist, 'filename')
    return path """

""" def downloadTracks(tracks, album: Album = None, playlist : Playlist=None):
    print('downloadTracks')
    def __getAlbum__(item: Track):
        album = TIDAL_API.getAlbum(item.album.id)
        if settings.saveCovers and not settings.usePlaylistFolder:
            scanCover(album)
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