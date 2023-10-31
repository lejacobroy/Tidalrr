#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   scanQueuesArtists.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''

from tidalrr.database import *
from tidalrr.tidal import *
from tidalrr.workers import *
from tidalrr.workers.scanQueuedAlbums import *
from tidalrr.workers.scanQueuedTracks import *

def scanQueuedPlaylists():
    playlists = getTidalPlaylists()
    if len(playlists) > 0 :
        for playlist in playlists:
            start_playlist(Playlist(*playlist))

def start_playlist_sync(UserId=None):
    playlists = TIDAL_API.getPlaylistsAndFavorites(UserId)
    for playlist in playlists:
        if playlist.title is not None:
            addTidalPlaylist(playlist)

def writePlaylistInfos(tracks, album: Album = None, playlist : Playlist=None):
    def __getAlbum__(item: Track):
        album = TIDAL_API.getAlbum(item.album.id)
        settings = getSettings()
        if settings.saveCovers and not settings.usePlaylistFolder:
            scanCover(album)
        return album
    
    for index, item in enumerate(tracks):
        itemAlbum = album
        if itemAlbum is None:
            itemAlbum = __getAlbum__(item)
            item.trackNumberOnPlaylist = index + 1
        addTidalTrack(item)


def start_playlist(obj: Playlist):
    print(obj)
    # here we have the playlist object, we can export it to json
    #print(aigpy.model.modelToDict(obj))
    # save this to playlist.json
    data = aigpy.model.modelToDict(obj)

    path = getPlaylistPath(obj)

    aigpy.file.write(str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.json', json.dumps(data), 'w+')

    print('Saved playlist json info to : '+str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.json')

    tracks = TIDAL_API.getItems(obj.uuid, Type.Playlist)
    for track in tracks:
        addTidalTrack(track)
    paths = []
    for index, item in enumerate(tracks):
        itemAlbum = getTidalAlbum(item.album)
        if itemAlbum is None:
            item.trackNumberOnPlaylist = index + 1
        paths.append(scanTrack(item, itemAlbum, obj)[1])

    with open(str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u', 'w') as f:
        #f.write('#EXTM3U\n')
        for i,item in enumerate(paths, start=1):
            f.write(str(getTrueHomePath())+'/'+item+'\n')
    print('Done generating m3u playlist file: '+str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u')

    # Generate the playlist file
    with open(str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u8', 'w') as f:
        f.write('#EXTM3U\n')
        for i,item in enumerate(aigpy.model.modelListToDictList(tracks), start=1):
            track = Track(*item)
            track.trackNumberOnPlaylist = i
            filename = path[i-1]
            f.write(f'#EXTINF:{item["duration"]},{item["artist"]["name"]} - {item["title"]}\n')
            f.write(str(getTrueHomePath())+'/'+filename+'\n') 
    print('Done generating m3u8 playlist file: '+str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u8')