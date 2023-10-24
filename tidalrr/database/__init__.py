#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   database.py
@Time    :   2023/10/18
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''# handles the database model
# create database table for the settings 
    # and migrate to it
# create database table for the tidal artists, albums, tracks, playlists 
    # and migrate to it
# create a database table for the downloaded content and link to tidal table
# create a database table for the queue 
    # and push/pull using workers
# split other functions to standalone workers
# webserver will use the database to show content and start workers 

import sqlite3
import os
from tidalrr.model import *
import json

database_path = os.path.abspath(os.path.dirname(__file__))+'/database.db'
schema_path = os.path.abspath(os.path.dirname(__file__))+'/schema.sql'

def createTables():
    connection = sqlite3.connect(database_path)
    with open(schema_path) as f:
        connection.executescript(f.read())
    cur = connection.cursor()
    cur.execute("INSERT INTO settings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ('{ArtistName}/{AlbumTitle} [{AlbumYear}] {Flag}', 
                 4,
                 'Max',
                 True,
                 True,
                 "./download",
                 True,
                 0,
                 True,
                 False,
                 'Playlist/{PlaylistName} [{PlaylistUUID}]',
                 True,
                 True,
                 True,
                 False,
                 '{TrackNumber} - {ArtistName} - {TrackTitle}{ExplicitFlag}',
                 False,
                 '',
                 '',
                 '',
                 '',
                 ''
                 )
                )
    connection.commit()
    connection.close()

def getSettings() -> Settings:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    settings = conn.execute('SELECT * FROM settings').fetchone()
    conn.close()
    return settings

def setSettings(settings=Settings()):
    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    cur.execute("UPDATE settings SET \
                albumFolderFormat = ?,\
                apiKeyIndex = ?,\
                audioQuality = ?,\
                checkExist = ?,\
                downloadDelay = ?,\
                downloadPath = ?,\
                includeEP = ?,\
                language = ?,\
                lyricFile = ?,\
                multiThread = ?,\
                playlistFolderFormat = ?,\
                saveAlbumInfo = ?,\
                saveCovers = ?,\
                showProgress = ?,\
                showTrackInfo = ?,\
                trackFileFormat = ?,\
                usePlaylistFolder = ?,\
                lidarrUrl = ?,\
                lidarrApi = ?,\
                tidalToken = ?,\
                plexUrl = ?,\
                plexToken = ?\
                ",(
                    settings.albumFolderFormat,
                    settings.apiKeyIndex,
                    settings.audioQuality,
                    settings.checkExist,
                    settings.downloadDelay,
                    settings.downloadPath,
                    settings.includeEP,
                    settings.language,
                    settings.lyricFile,
                    settings.multiThread,
                    settings.playlistFolderFormat,
                    settings.saveAlbumInfo,
                    settings.saveCovers,
                    settings.showProgress,
                    settings.showTrackInfo,
                    settings.trackFileFormat,
                    settings.usePlaylistFolder,
                    settings.lidarrUrl,
                    settings.lidarrApi,
                    settings.tidalToken,
                    settings.plexUrl,
                    settings.plexToken
                    ))
    connection.commit()
    connection.close()

def setToken(token=str):
    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    cur.execute("UPDATE settings SET tidalToken = ?",( token, ))
    connection.commit()
    connection.close()

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

def addTidalQueue(queue=Queue):
    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_queue VALUES (?, ?, ?, ?, ?, ?)",
                (
                    queue.url,
                    queue.type,
                    queue.login,
                    queue.id,
                    queue.path,
                    queue.encryptionKey
                ))
    connection.commit()
    connection.close()

def convertToQueue(queue) -> Queue:
    queueType = Queue(
        id= queue['id'],
        login= queue['login'],
        type= queue['type'],
        path= queue['path'],
        url= queue['url'],
        encryptionKey= queue['encryptionKey']
    )
    return queueType

def getTidalQueues(type=str) -> [Queue]:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    if type == '':
        rows = conn.execute('SELECT * FROM tidal_queue').fetchall()
    else:
        rows = conn.execute('SELECT * FROM tidal_queue WHERE type = ?', (type,)).fetchall()
    conn.close()
    queues = []
    for i, q in enumerate(rows):
        queues.append(convertToQueue(q))
    return queues

def delTidalQueue(path=str):
    conn = sqlite3.connect(database_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM tidal_queue WHERE path = ?', (path,))
    conn.commit()
    conn.close()

def addFiles(file=File):
    connection = sqlite3.connect(database_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO files VALUES (?, ?, ?, ?)",
                (
                    file.description,
                    file.type,
                    file.id,
                    file.path
                ))
    connection.commit()
    connection.close()

def getFiles() -> [File]:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM files').fetchall()
    conn.close()
    return rows