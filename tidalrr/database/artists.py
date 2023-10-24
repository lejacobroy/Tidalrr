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

def addTidalArtist(artist=Artist):
    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_artists VALUES (?, ?, ?)",
                (artist.id, artist.name, artist.url))
    connection.commit()
    connection.close()

def convertToArtist(artist) -> Artist:
        artistType = Artist(
            id= artist['id'],
            name= artist['name'],
            url= artist['url']
        )
        return artistType

def getTidalArtists() -> [Artist]:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_artists WHERE id IS NOT NULL').fetchall()
    conn.close()
    new_rows = [Artist]
    for i, item in enumerate(rows):
        new_rows.append(convertToArtist(item))
    return rows

def getTidalArtist(id=int) -> Artist:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM tidal_artists WHERE id = ?', (id,)).fetchone()
    conn.close()
    return convertToArtist(row)

def getArtistsNameJSON(artists):
        array = []
        for item in json.loads(artists):
            array.append(item["name"])
        return ", ".join(array)