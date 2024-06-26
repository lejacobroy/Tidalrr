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
import aigpy
import json
from tidalrr.model import Track, Track, Playlist
from tidalrr.tidal import TIDAL_API, Type
from tidalrr.database import getSettings
from tidalrr.database.tracks import getTidalTrack, addTidalTrack, updateTidalTrack
from tidalrr.database.albums import addTidalAlbum
from tidalrr.database.artists import addTidalArtist
from tidalrr.database.playlists import getMonitoredTidalPlaylists, getTidalPlaylistTracks, addTidalPlaylistTrack

import logging

logger = logging.getLogger(__name__)

def scanQueuedPlaylists():
    try:
        playlists = getMonitoredTidalPlaylists()
        if len(playlists) > 0:
            for i, playlist in enumerate(playlists):
                try:
                    if hasattr(playlist, 'uuid'):
                        if playlist.monitored:
                            print('Scanning playlist ', str(i), ' / ',str(len(playlists)), playlist.title)
                            start_playlist(playlist)
                except Exception as e:
                    print("Error scanning playlist: ", e)
    except Exception as e:
        print("Error getting playlists: ", e)


def start_playlist(playlist: Playlist):
    settings = getSettings()
    aigpy.path.mkdirs(settings.downloadPath+'/Playlists')

    print('Scanning playlist ',playlist.title)
    tracks = TIDAL_API.getItems(playlist.uuid, Type.Playlist)
    
    # list only the tracks not downloaded
    tracksToScan, paths = verifyPlaylistTracks(playlist, tracks)

    # Save playlist info to JSON
    generateJSonFile(playlist)

def verifyPlaylistTracks(playlist: Playlist, tidalTracks: list[Track]):
    savedTracks = getTidalPlaylistTracks(playlist.uuid)
    tracksToScan = []
    paths = []

    for i, tidalTrack in enumerate(tidalTracks):
        exists = False
        for savedTrack in savedTracks:
            if hasattr(savedTrack, 'id') and tidalTrack.id == savedTrack.id:
                if savedTrack.queued or savedTrack.downloaded:
                    exists = True
        if not exists:
            # track not linked to playlist
            dbTrack = getTidalTrack(tidalTrack.id)
            if not hasattr(dbTrack, 'id'):
                # track not in database
                # also, add it to the db
                tidalTrack.queued = True
                addTidalTrack(tidalTrack)
                # add artist and album to the db
                try:
                    tidal_artist = TIDAL_API.getArtist(tidalTrack.artist)
                    addTidalArtist(tidal_artist)
                    print('Added artist ', tidalTrack.artist)
                except Exception as e:
                    print('Error adding artist to DB: ', e)
                try:
                    tidal_album = TIDAL_API.getAlbum(tidalTrack.album)
                    addTidalAlbum(tidal_album)
                    print('Added album ', tidalTrack.album)
                except Exception as e:
                    print('Error adding album to DB: ', e)
                    
                tracksToScan.append(tidalTrack)
            elif dbTrack.queued == 0 and dbTrack.downloaded == 0:
                tidalTrack.queued = True
                updateTidalTrack(tidalTrack)
                tracksToScan.append(tidalTrack)

            addTidalPlaylistTrack(playlist.uuid, tidalTrack.id)
            print('Added missing track '+str(i)+'/'+str(len(tidalTracks))+' to DB: '+tidalTrack.title)
        paths.append(tidalTrack.path)

    return tracksToScan, paths

def generateJSonFile(playlist: Playlist):
    aigpy.file.write(playlist.path+'.json', json.dumps(playlist, default=lambda x: x.__dict__), 'w+')

    print('Saved playlist json info to : '+playlist.path+'.json')