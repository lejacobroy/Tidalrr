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
from tidalrr.workers.scanQueuedAlbums import scanQueuedAlbums

import logging

logger = logging.getLogger(__name__)

def scanMissingArtists():
    tracks = getTidalTracksUnordered()
    for i, track in enumerate(tracks):
        if hasattr(track, 'artist'):
            artist = getTidalArtist(track.artist)
            if artist is None:
                try:
                    tidal_artist = TIDAL_API.getArtist(track.artist)
                    addTidalArtist(tidal_artist)
                    print('Added artist ', track.artist)
                except Exception as e:
                    print('Error adding artist to DB: ', e)
                
        if hasattr(track, 'album'):
            album = getTidalAlbum(track.album)
            if album is None:
                try:
                    tidal_album = TIDAL_API.getAlbum(track.album)
                    addTidalAlbum(tidal_album)
                    print('Added album ', track.album)
                except Exception as e:
                    print('Error adding album to DB: ', e)


def scanQueuedArtists():
    scanMissingArtists()
    artists = getMonitoredTidalArtists()
    if len(artists) > 0:
        for i, artist in enumerate(artists):
            try:
                if hasattr(artist, 'id'):
                    print('Scanning artist ', str(i), ' / ', str(len(artists)), artist.name)
                    start_artist(artist)
                    #artist.monitored = False
                    #updateTidalArtist(artist)
            except Exception as e:
                print("Error scanning artist: ", e)
                if "Artist" in str(e) and "not found" in str(e):
                    artist.monitored = False
                    updateTidalArtist(artist)


def start_artist(obj: Artist):
    settings = getSettings()
    albums = TIDAL_API.getArtistAlbums(obj.id, settings.includeEP)
    if len(albums) > 0 :
        for i,album in enumerate(albums):
            if hasattr(album, 'id'):
                existing = getTidalAlbum(album.id)
                if existing is None:
                    if not hasattr(getTidalArtist(album.artist), 'id'):
                        # insert artist in db
                        addTidalArtist(TIDAL_API.getArtist(album.artist))
                    print('Adding album to DB  '+str(i)+'/'+str(len(albums))+' '+obj.name+' - '+album.title)
                    if obj.monitored:
                        # artist is monitored, we will monitor this album too
                        album.monitored = True
                    addTidalAlbum(album)
                    #scanQueuedAlbums()
