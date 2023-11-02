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
from tidalrr.model import *
from pathlib import Path

db_path = Path(__file__).parent.joinpath('config/database.db').absolute()

def addTidalArtist(artist=Artist):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_artists VALUES (?, ?, ?, ?, ?, ?)",
                (artist.id, artist.name, artist.url, artist.path, artist.queued, artist.downloaded))
    connection.commit()
    connection.close()

def updateTidalArtist(artist=Artist):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_artists SET queued = ?, downloaded = ? WHERE id = ?",
                (artist.queued, artist.downloaded, artist.id))
    connection.commit()
    connection.close()

def updateTidalArtistsDownloaded():
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_artists SET queued = 0, downloaded = 1 WHERE id IN (\
                    SELECT tidal_artists.id\
                    FROM tidal_artists\
                    LEFT JOIN tidal_albums ON tidal_albums.artist = tidal_artists.id\
                    GROUP BY tidal_artists.id\
                    HAVING COUNT(*) = SUM(CASE WHEN tidal_albums.downloaded = TRUE THEN 1 ELSE 0 END)\
                )")
    connection.commit()
    connection.close()

def getTidalArtists() -> [Artist]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_artists WHERE id IS NOT NULL').fetchall()
    conn.close()
    new_rows = [Artist]
    if len(rows) > 0 :
        for item in rows:
            new_rows.append(convertToArtist(item))
    return new_rows

def getTidalArtist(id=int) -> Artist:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM tidal_artists WHERE id = ?', (id,)).fetchone()
    conn.close()
    artist = None
    if row is not None:
        artist = convertToArtist(row)
    return artist