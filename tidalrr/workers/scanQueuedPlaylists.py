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
import time
from tidalrr.database import *
from tidalrr.tidal import *
from tidalrr.workers import *
from tidalrr.workers.scanQueuedAlbums import *
from tidalrr.workers.scanQueuedTracks import *

import logging

logger = logging.getLogger(__name__)

def scanQueuedPlaylists():
    try:
        playlists = getTidalPlaylists()
        if len(playlists) > 0:
            for i, playlist in enumerate(playlists):
                try:
                    if hasattr(playlist, 'uuid'):
                        if playlist.monitored:
                            print('Scanning playlist ', str(i), ' / ',str(len(playlists)), playlist.title)
                            start_playlist(playlist)
                            #playlist.monitored = False
                            #updateTidalPlaylist(playlist)
                except Exception as e:
                    print("Error scanning playlist: ", e)
    except Exception as e:
        print("Error getting playlists: ", e)


def start_playlist(obj: Playlist):
    # save this to playlist.json
    #path = getPlaylistPath(obj)
    settings = getSettings()
    aigpy.path.mkdirs(settings.downloadPath+'/Playlists')

    paths = []
    tracks = TIDAL_API.getItems(obj.uuid, Type.Playlist)
    print('Scanning playlist ',obj.title,' should take ', len(tracks)*3/60,' minutes')
    savedTracks = getTidalPlaylistTracks(obj.uuid)
    for index,track in enumerate(tracks):
        skip = False
        if hasattr(track, 'id'):
            for i, savedTrack in enumerate(savedTracks):
                if hasattr(savedTrack, 'id') and track.id == savedTrack.id:
                    print('Track '+str(index)+'/'+str(len(tracks))+' already in database and linked to playlist, skipping')
                    paths.append(savedTrack.path)
                    addTidalPlaylistTrack(obj.uuid, track.id)
                    skip = True
                    break # skip the outer loop
            if not skip and index > 200:
                # adding more pause time between tracks for longer playlists
                time.sleep(5)
            #check if artist exists
            if not skip and not hasattr(getTidalArtist(track.artist), 'id'):
                # insert artist in db
                try:
                    trackArtist = TIDAL_API.getArtist(track.artist)
                    addTidalArtist(trackArtist)
                except:
                    print('Track artist dosent exist on Tidal, skipping track')
                    continue
            #same for album
            if not skip and not hasattr(getTidalAlbum(track.album), 'id'):
                # insert artist in db
                addTidalAlbum(TIDAL_API.getAlbum(track.album))
            if obj.monitored:
                # playlist is monitored, we will queue this track too
                track.queued = True
            addTidalTrack(track)
            addTidalPlaylistTrack(obj.uuid, track.id)
            print('Adding track '+str(index)+ '/'+str(len(tracks))+' to DB: '+track.title)
            itemAlbum = getTidalAlbum(track.album)
            if itemAlbum is None:
                track.trackNumberOnPlaylist = index + 1
            time.sleep(2)
            if not skip:
                path = scanTrackPath(track, itemAlbum, obj)[1]
            else:
                existingTrack = getTidalTrack(track.id)
                path = existingTrack.path
                
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
                itemPath = Path(item.replace('.mp4','.flac'))
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
                    itemPath = Path(item.path.replace(settings.downloadPath, plexPath).replace('.mp4','.flac'))
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
