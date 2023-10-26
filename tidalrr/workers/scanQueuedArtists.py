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
from tidalrr.settings import *
from tidalrr.tidal import *
from tidalrr.workers import *

def scanQueuedArtists():
    artists = getTidalArtists()
    if len(artists) > 0 :
        for i, artist in enumerate(artists):
            if hasattr(artist, 'id'):
                print('Scanning artist '+ str(i)+'/'+str(len(artists))+' '+artist.name)
                start_artist(artist)

def start_artist(obj: Artist):
    albums = TIDAL_API.getArtistAlbums(obj.id, SETTINGS.includeEP)
    if len(albums) > 0 :
        for i,album in enumerate(albums):
            print('Adding album to DB  '+str(i)+'/'+str(len(albums))+' '+obj.name+' - '+album.title)
            addTidalAlbum(album)
