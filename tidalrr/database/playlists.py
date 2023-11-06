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

def addTidalPlaylist(playlist=Playlist):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_playlists VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    playlist.uuid,
                    playlist.title,
                    playlist.duration,
                    playlist.numberOfTracks,
                    playlist.description,
                    playlist.image,
                    playlist.squareImage,
                    playlist.url,
                    playlist.path,
                    playlist.queued,
                    playlist.downloaded,
                ))
    connection.commit()
    connection.close()

def addTidalPlaylistTrack(uuid=str, track=int):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_playlist_tracks VALUES (?, ?, ?)",
                (
                    uuid,
                    track,
                    ''
                ))
    connection.commit()
    connection.close()

def getTidalPlaylists() -> [Playlist]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_playlists WHERE uuid IS NOT NULL').fetchall()
    conn.close()
    new_rows = [Playlist]
    if len(rows) > 0 :
        for item in rows:
            new_rows.append(convertToPlaylist(item))
    return new_rows

def getTidalPlaylist(id=str) -> Playlist:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM tidal_playlists WHERE uuid = ?', (id,)).fetchone()
    conn.close()
    playlist = None
    if row is not None:
        playlist = convertToPlaylist(row)
    return playlist

def getTidalPlaylistDownloaded() -> [Playlist]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_playlists WHERE downloaded = 1').fetchall()
    conn.close()
    new_rows = [Playlist]
    if len(rows) > 0 :
        for item in rows:
            new_rows.append(convertToPlaylist(item))
    return new_rows

def getTidalPlaylistTracks(uuid=str) -> [Track]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT tidal_tracks.* FROM tidal_tracks\
                       inner join tidal_playlist_tracks ON tidal_playlist_tracks.track = tidal_tracks.id \
                       WHERE tidal_playlist_tracks.uuid = ?', (uuid,)).fetchall()
    conn.close()
    new_rows = [Track]
    if len(rows) > 0 :
        for item in rows:
            new_rows.append(convertToTrack(item))
    return new_rows

def updateTidalPlaylist(playlist=Playlist):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_playlists SET queued = ?, downloaded = ?, plexUUID = ? WHERE uuid = ?",
                (playlist.queued, playlist.downloaded, playlist.plexUUID, playlist.uuid))
    connection.commit()
    connection.close()

def updateTidalPlaylistTrack(uuid:str, id:int, puid:str):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_playlist_tracks SET puid = ? WHERE uuid = ? AND track = ?",
                (puid, uuid, id))
    connection.commit()
    connection.close()

def updateTidalPlaylistsDownloaded():
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_playlists SET queued = 0, downloaded = 1 WHERE uuid IN (\
                    SELECT tidal_playlists.uuid\
                    FROM tidal_playlists\
                    inner join tidal_playlist_tracks ON tidal_playlist_tracks.uuid = tidal_playlists.uuid\
                    LEFT JOIN tidal_tracks ON tidal_playlist_tracks.track = tidal_tracks.id\
                    GROUP BY tidal_playlists.uuid\
                    HAVING COUNT(*) = SUM(CASE WHEN tidal_tracks.downloaded = TRUE THEN 1 ELSE 0 END)\
                )")
    connection.commit()
    connection.close()