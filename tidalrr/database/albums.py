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
from tidalrr.model import Album, convertToAlbum, getArtistsNameJSON
from pathlib import Path

db_path = Path(__file__).parent.joinpath('config/database.db').absolute()

def addTidalAlbum(album=Album):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_albums (id, title, duration, numberOfTracks, numberofVolumes, releaseDate, type, version, cover, explicit, audioQuality, audioModes,artist, artists, url ,path, monitored, downloaded)\
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                    album.monitored,
                    album.downloaded
                ))
    connection.commit()
    connection.close()

def updateTidalAlbum(album=Album):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_albums SET monitored = ?, downloaded = ? WHERE id = ?",
                (album.monitored, album.downloaded, album.id))
    connection.commit()
    connection.close()

def updateTidalAlbumsDownloaded():
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_albums SET downloaded = 1 WHERE id IN (\
                    SELECT tidal_albums.id\
                    FROM tidal_albums\
                    LEFT JOIN tidal_tracks ON tidal_tracks.album = tidal_albums.id\
                    GROUP BY tidal_albums.id\
                    HAVING COUNT(*) = SUM(CASE WHEN tidal_tracks.downloaded = TRUE OR tidal_tracks.queued = FALSE THEN 1 ELSE 0 END)\
                )")
    connection.commit()
    connection.close()

def getTidalAlbums() -> list[Album]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT tidal_albums.* FROM tidal_albums \
                        inner join tidal_artists on tidal_artists.id = tidal_albums.artist \
                        WHERE tidal_albums.title <> ""\
                        ORDER BY tidal_artists.name, tidal_albums.title').fetchall()
    new_rows = []
    conn.close()
    if len(rows) > 0 :
        for album in rows:
            a = convertToAlbum(album)
            a.artists = getArtistsNameJSON(a.artists)
            new_rows.append(a)
    return new_rows

def getMonitoredTidalAlbums() -> list[Album]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT tidal_albums.* FROM tidal_albums \
                        inner join tidal_artists on tidal_artists.id = tidal_albums.artist \
                        WHERE tidal_albums.title <> "" AND tidal_albums.monitored = 1 \
                        ORDER BY tidal_artists.name, tidal_albums.title').fetchall()
    new_rows = []
    conn.close()
    if len(rows) > 0 :
        for album in rows:
            a = convertToAlbum(album)
            a.artists = getArtistsNameJSON(a.artists)
            new_rows.append(a)
    return new_rows

def getAlbumsForArtist(artistId) -> list[Album]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT tidal_albums.* FROM tidal_albums \
                        inner join tidal_artists on tidal_artists.id = tidal_albums.artist \
                        WHERE tidal_albums.title <> "" AND tidal_albums.artist = ? \
                        ORDER BY tidal_artists.name, tidal_albums.title', (artistId,)).fetchall()
    new_rows = []
    conn.close()
    if len(rows) > 0 :
        for album in rows:
            a = convertToAlbum(album)
            a.artists = getArtistsNameJSON(a.artists)
            new_rows.append(a)
    return new_rows

def getTidalAlbum(id=int) -> Album:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM tidal_albums WHERE id = ?', (id,)).fetchone()
    conn.close()
    album = None
    if row is not None:
        album = convertToAlbum(row)
        album.artists = getArtistsNameJSON(album.artists)
    return album

def getNumDownloadedAlbumTracks(albumId):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT COUNT(*) FROM tidal_tracks WHERE album = ? and downloaded = 1', (albumId,)).fetchone()
    conn.close()
    return row[0]