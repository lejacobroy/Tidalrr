#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   database.py
@Time    :   2023/10/18
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import sqlite3
from tidalrr.definitions import DB_PATH
from tidalrr.model import *

def addTidalPlaylist(playlist=Playlist):
    connection = sqlite3.connect(DB_PATH)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_playlists VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    playlist.id,
                    playlist.title,
                    playlist.duration,
                    playlist.numberOfTracks,
                    playlist.description,
                    playlist.image,
                    playlist.squareImage,
                    playlist.url
                ))
    connection.commit()
    connection.close()

def getTidalPlaylists() -> [Playlist]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_playlists WHERE id IS NOT NULL').fetchall()
    conn.close()
    return rows