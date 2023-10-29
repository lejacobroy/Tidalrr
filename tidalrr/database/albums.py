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

database_path = os.path.abspath(os.path.dirname(__file__))+'/../config/database.db'
schema_path = os.path.abspath(os.path.dirname(__file__))+'/schema.sql'

def addTidalAlbum(album=Album):
    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_albums VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    album.id,
                    album.title,
                    album.duration,
                    album.numberOfTracks,
                    album.numberOfVolumes,
                    album.releaseDate,
                    album.type,
                    album.version,
                    album.cover,
                    album.explicit,
                    album.audioQuality,
                    album.audioModes,
                    album.artist,
                    album.artists,
                    album.url,
                    album.path,
                    album.queued,
                    album.downloaded
                ))
    connection.commit()
    connection.close()

def updateTidalAlbum(album=Album):
    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_albums SET queued = ?, downloaded = ? WHERE id = ?",
                (album.queued, album.downloaded, album.id))
    connection.commit()
    connection.close()

def updateTidalAlbumsDownloaded():
    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_albums SET queued = 0, downloaded = 1 WHERE id IN (\
                    SELECT tidal_albums.id\
                    FROM tidal_albums\
                    LEFT JOIN tidal_tracks ON tidal_tracks.album = tidal_albums.id\
                    GROUP BY tidal_albums.id\
                    HAVING COUNT(*) = SUM(CASE WHEN tidal_tracks.downloaded = TRUE THEN 1 ELSE 0 END)\
                )")
    connection.commit()
    connection.close()

def getArtistsNameJSON(artists):
        array = []
        for item in json.loads(artists):
            array.append(item["name"])
        return ", ".join(array)

def getTidalAlbums() -> [Album]:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_albums WHERE title <> ""').fetchall()
    new_rows = [Album]
    conn.close()
    if len(rows) > 0 :
        for album in rows:
            a = convertToAlbum(album)
            a.artists = getArtistsNameJSON(a.artists)
            new_rows.append(a)
    return new_rows

def getTidalAlbum(id=int) -> Album:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM tidal_albums WHERE id = ?', (id,)).fetchone()
    conn.close()
    album = None
    if row is not None:
        album = convertToAlbum(row)
        album.artists = getArtistsNameJSON(album.artists)
    return album