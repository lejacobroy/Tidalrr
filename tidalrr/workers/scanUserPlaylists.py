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
from tidalrr.workers.scanQueuedPlaylists import *

def scanUserPlaylists(UserId=None):
    playlists = TIDAL_API.getPlaylistsAndFavorites(UserId)
    for i,playlist in enumerate(playlists):
        if hasattr(playlist, 'title'):
            playlist.queued = True
            addTidalPlaylist(playlist)
            print('Added User playlist to DB '+ str(i)+'/'+str(len(playlists))+' '+playlist.title)
            scanQueuedPlaylists()