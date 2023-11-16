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
import logging

logger = logging.getLogger(__name__)

def scanUserPlaylists(UserId=None):
  print("Starting scan of user playlists")
  
  try:
    playlists = TIDAL_API.getPlaylistsAndFavorites(UserId)
  except Exception as e:
    print("Error getting playlists: %s", e)
    raise

  for i,playlist in enumerate(playlists):
    try:
      if hasattr(playlist, 'title'):
        playlist.queued = True
        addTidalPlaylist(playlist)
        print('Added playlist %s to DB', playlist.title) 
    except Exception as e:
      print("Error adding playlist: %s", e)

  try:  
    scanQueuedPlaylists()
    print("Completed scan of user playlists")
  except Exception as e:
    print("Error scanning queued playlists: %s", e)
