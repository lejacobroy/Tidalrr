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

database_path = os.path.abspath(os.path.dirname(__file__))+'/database.db'
schema_path = os.path.abspath(os.path.dirname(__file__))+'/schema.sql'

def addTidalAlbum(album=Album):
    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_albums VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                    json.dumps(album.audioModes),
                    album.artist,
                    json.dumps(album.artists),
                    album.url
                ))
    connection.commit()
    connection.close()

def convertToAlbum(album) -> Album:
    albumType = Album(
           id= album['id'],
           title= album['title'],
           releaseDate= album['releaseDate'],
           type= album['type'],
           cover= album['cover'],
           explicit= album['explicit'],
           audioQuality= album['audioQuality'],
           audioModes= album['audioModes'],
           path= '',
           artist= album['artist'],
           artists= album['artists'],
           url= album['url'],
           duration= album['duration'],
           numberOfTracks=  album['numberOfTracks'],
           numberOfVolumes= album['numberOfVolumes'],
           version= album['version']
        )
    return albumType

def getTidalAlbums() -> [Album]:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_albums WHERE title IS NOT ""').fetchall()
    new_rows = [Album]
    for i, album in enumerate(rows):
        new_rows.append(convertToAlbum(album))
    conn.close()
    return new_rows

def getTidalAlbum(id=int) -> Album:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM tidal_albums WHERE id = ?', (id,)).fetchone()
    conn.close()
    return convertToAlbum(row)