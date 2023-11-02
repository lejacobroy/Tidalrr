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

from tidalrr.database.albums import getArtistsNameJSON

def addTidalTrack(track=Track):
    connection = sqlite3.connect(DB_PATH)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_tracks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                    track.audioModes,
                    track.copyRight,
                    track.artist,
                    track.artists,
                    track.album,
                    track.url,
                    track.path,
                    track.queued,
                    track.downloaded
                ))
    connection.commit()
    connection.close()

def updateTidalTrack(track=Track):
    connection = sqlite3.connect(DB_PATH)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_tracks SET queued = ?, downloaded = ? WHERE id = ?",
                (track.queued, track.downloaded, track.id))
    connection.commit()
    connection.close()

def getTidalTracks() -> [Track]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_tracks WHERE id IS NOT NULL').fetchall()
    conn.close()
    new_rows = []
    if len(rows) > 0:
        for track in rows:
            t = convertToTrack(track)
            t.artists = getArtistsNameJSON(t.artists)
            new_rows.append(t)
    return new_rows

def getTidalTrack(id=int) -> Track:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM tidal_tracks WHERE id = ?',(id,)).fetchone()
    conn.close()
    track = None
    if row is not None:
        track = convertToTrack(row)
        track.artists = getArtistsNameJSON(track.artists)
    return track