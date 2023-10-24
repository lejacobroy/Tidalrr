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

def convertToTrack(track) -> Track:
    trackType = Track(
        id= track['id'],
        title= track['title'],
        duration= track['duration'],
        trackNumber= track['trackNumber'],
        volumeNumber= track['volumeNumber'],
        trackNumberOnPlaylist= '',
        version= track['version'],
        isrc= track['isrc'],
        explicit= track['explicit'],
        audioQuality= track['audioQuality'],
        audioModes= track['audioModes'],
        copyRight= track['copyright'],
        artist= track['artist'],
        artists= track['artists'],
        album= track['album'],
        allowStreaming='',
        playlist='',
        url= track['url'],
    )
    return trackType

def addTidalTrack(track=Track):
    print(track.title)
    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    track.id,
                    track.title,
                    track.duration,
                    track.trackNumber,
                    track.volumeNumber,
                    track.trackNumberOnPlaylist,
                    track.version,
                    track.isrc,
                    track.explicit,
                    track.audioQuality,
                    json.dumps(track.audioModes),
                    track.copyRight,
                    track.artist,
                    json.dumps(track.artists),
                    track.album,
                    track.url
                ))
    connection.commit()
    connection.close()
    print('done')

def getTidalTracks() -> [Track]:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_tracks WHERE id IS NOT NULL').fetchall()
    conn.close()
    new_rows = []
    for track in rows:
        new_rows.append(convertToTrack(track))
    return new_rows

def getTidalTrack(id=int) -> Track:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM tidal_tracks WHERE id = ?',(id,)).fetchone()
    conn.close()
    return convertToTrack(row)