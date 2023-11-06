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
import pathlib
from tidalrr.database import *
from tidalrr.tidal import *
from tidalrr.workers import *
from tidalrr.workers.scanQueuedAlbums import *
from tidalrr.workers.scanQueuedTracks import *

def scanQueuedPlaylists():
    playlists = getTidalPlaylists()
    if len(playlists) > 0 :
        for i,playlist in enumerate(playlists):
            if hasattr(playlist, 'uuid'):
                if playlist.queued:
                    print('Scanning playlist '+ str(i)+'/'+str(len(playlists))+' '+playlist.title)
                    start_playlist(playlist)
                    playlist.queued = False
                    updateTidalPlaylist(playlist)

def start_playlist(obj: Playlist):
    # save this to playlist.json
    #path = getPlaylistPath(obj)
    settings = getSettings()
    aigpy.path.mkdirs(settings.downloadPath+'/Playlists')

    paths = []
    tracks = TIDAL_API.getItems(obj.uuid, Type.Playlist)
    savedTracks = getTidalPlaylistTracks(obj.uuid)
    for index,track in enumerate(tracks):
        if hasattr(track, 'id'):
            for i, savedTrack in enumerate(savedTracks):
                if hasattr(savedTrack, 'id') and track.id == savedTrack.id:
                    paths.append(savedTrack.path)
                    addTidalPlaylistTrack(obj.uuid, track.id)
                    break # skip the outer loop
            #check if artist exists
            if not hasattr(getTidalArtist(track.artist), 'id'):
                # insert artist in db
                try:
                    trackArtist = TIDAL_API.getArtist(track.artist)
                    addTidalArtist(trackArtist)
                except:
                    print('Track artist dosent exist on Tidal, skipping track')
                    continue
            #same for album
            if not hasattr(getTidalAlbum(track.album), 'id'):
                # insert artist in db
                addTidalAlbum(TIDAL_API.getAlbum(track.album))

            track.queued = True
            addTidalTrack(track)
            addTidalPlaylistTrack(obj.uuid, track.id)

            itemAlbum = getTidalAlbum(track.album)
            if itemAlbum is None:
                track.trackNumberOnPlaylist = index + 1
            path = scanTrackPath(track, itemAlbum, obj)[1]
            if path != '':
                paths.append(path)

    aigpy.file.write(obj.path+'.json', json.dumps(obj, default=lambda x: x.__dict__), 'w+')

    print('Saved playlist json info to : '+obj.path+'.json')
    plexPath = ''
    if settings.plexToken != '' and settings.plexUrl != '' and settings.plexHomePath != '':
        plexPath = settings.plexHomePath
    with open(obj.path+'.m3u', 'w+') as f:
        for i,item in enumerate(paths, start=1):
            if len(item) > 0:
                itemPath = Path(item)
                if plexPath != '':
                    itemPath = Path(item.replace(settings.downloadPath, plexPath).replace('.mp4','.flac'))
                f.write(os.path.join(itemPath)+'\n')
    print('Generated m3u playlist file: '+obj.path+'.m3u')

    # Generate the playlist file
    with open(obj.path+'.m3u8', 'w+') as f:
        f.write('#EXTM3U\n')
        for i,item in enumerate(tracks, start=1):
            artist = getTidalArtist(item.artist)
            if hasattr(artist, 'id'):
                f.write(f'#EXTINF:{item.duration},{artist.name} - {item.title}\n')
                itemPath = Path(item.path.replace('.mp4','.flac'))
                if plexPath != '':
                    itemPath = Path(item.replace(settings.downloadPath, plexPath))
                f.write(os.path.join(itemPath)+'\n')
    print('Generated m3u8 playlist file: '+obj.path+'.m3u8')
    scanQueuedTracks()

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
