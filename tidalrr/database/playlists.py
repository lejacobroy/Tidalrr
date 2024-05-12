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
from tidalrr.model import Playlist, convertToPlaylist, Track, convertToTrack, getArtistsNameJSON
from pathlib import Path

db_path = Path(__file__).parent.joinpath('config/database.db').absolute()

def addTidalPlaylist(playlist=Playlist):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_playlists (uuid, title, duration, numberOfTracks, description, image, squareimage, url, path, monitored, downloaded, plexUUID) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                    playlist.monitored,
                    playlist.downloaded,
                    playlist.plexUUID
                ))
    connection.commit()
    connection.close()

def addTidalPlaylistTrack(uuid=str, track=int):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_playlist_tracks (uuid, track, puid) VALUES (?, ?, ?)",
                (
                    uuid,
                    track,
                    ''
                ))
    connection.commit()
    connection.close()

def getTidalPlaylists() -> list[Playlist]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_playlists WHERE uuid IS NOT NULL').fetchall()
    conn.close()
    new_rows = []
    if len(rows) > 0 :
        for item in rows:
            new_rows.append(convertToPlaylist(item))
    return new_rows

def getMonitoredTidalPlaylists() -> list[Playlist]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_playlists WHERE uuid IS NOT NULL AND monitored = 1').fetchall()
    conn.close()
    new_rows = []
    if len(rows) > 0 :
        for item in rows:
            new_rows.append(convertToPlaylist(item))
    return new_rows

def getDownloadedTidalPlaylists() -> list[Playlist]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM tidal_playlists WHERE uuid IS NOT NULL AND downloaded = TRUE').fetchall()
    conn.close()
    new_rows = []
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

def getTidalPlaylistTracks(uuid=str) -> list[Track]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT tidal_tracks.* FROM tidal_tracks\
                       inner join tidal_playlist_tracks ON tidal_playlist_tracks.track = tidal_tracks.id \
                       WHERE tidal_playlist_tracks.uuid = ?', (uuid,)).fetchall()
    conn.close()
    new_rows = []
    if len(rows) > 0 :
        for item in rows:
            a = convertToTrack(item)
            a.artists = getArtistsNameJSON(a.artists)
            new_rows.append(a)
    return new_rows


def updateTidalPlaylist(playlist=Playlist):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_playlists SET monitored = ?, downloaded = ?, plexUUID = ? WHERE uuid = ?",
                (playlist.monitored, playlist.downloaded, playlist.plexUUID, playlist.uuid))
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
    cur.execute("UPDATE tidal_playlists SET downloaded = 1 WHERE uuid IN (\
                    SELECT tidal_playlists.uuid\
                    FROM tidal_playlists\
                    inner join tidal_playlist_tracks ON tidal_playlist_tracks.uuid = tidal_playlists.uuid\
                    left JOIN tidal_tracks ON tidal_playlist_tracks.track = tidal_tracks.id\
                    WHERE tidal_playlists.uuid IN (\
                        select tidal_playlists.uuid\
                            FROM tidal_playlists\
                            inner join tidal_playlist_tracks ON tidal_playlist_tracks.uuid = tidal_playlists.uuid\
                            inner JOIN tidal_tracks ON tidal_playlist_tracks.track = tidal_tracks.id\
                                AND tidal_tracks.downloaded = 1\
						GROUP BY tidal_playlists.uuid\
                        having COUNT(tidal_tracks.id) > 0)\
                    GROUP BY tidal_playlists.uuid\
                    HAVING COUNT(*) = SUM(CASE WHEN tidal_tracks.downloaded = TRUE OR tidal_tracks.queued = FALSE THEN 1 ELSE 0 END)\
                )")
    connection.commit()
    connection.close()

def updateTidalPlaylistTracksPlexUUID(uuid:str):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_playlist_tracks \
                SET puid = track.plexUUID \
                FROM (select id, plexUUID from tidal_tracks) as track\
                WHERE  track.id =  tidal_playlist_tracks.track \
                AND track.plexUUID != tidal_playlist_tracks.puid \
                AND tidal_playlist_tracks.uuid = ? ", (uuid,))
    connection.commit()
    connection.close()

def getNumDownloadedPlaylistTracks(PlaylistUUID):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT COUNT(tidal_tracks.id) FROM tidal_tracks\
                       inner join tidal_playlist_tracks ON tidal_playlist_tracks.track = tidal_tracks.id \
                       WHERE tidal_playlist_tracks.uuid = ? and tidal_tracks.downloaded = 1', (PlaylistUUID,)).fetchone()
    conn.close()
    return row[0]