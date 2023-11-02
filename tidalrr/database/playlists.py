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
import os
from tidalrr.model import *
import json

database_path = os.path.abspath(os.path.dirname(__file__))+'/../../config/database.db'
schema_path = os.path.abspath(os.path.dirname(__file__))+'/schema.sql'

def addTidalPlaylist(playlist=Playlist):
    connection = sqlite3.connect(database_path)
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
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_playlists WHERE id IS NOT NULL').fetchall()
    conn.close()
    return rows