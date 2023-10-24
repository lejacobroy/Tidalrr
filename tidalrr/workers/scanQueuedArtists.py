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
    tidalrrStart()
    artists = getTidalArtists()
    for i, artist in enumerate(artists):
        start_artist(Artist(*artist))

def start_artist(obj: Artist):
    albums = TIDAL_API.getArtistAlbums(obj.id, SETTINGS.includeEP)
    for album in albums:
        addTidalAlbum(album)

scanQueuedArtists()