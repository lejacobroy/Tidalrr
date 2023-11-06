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
from tidalrr.database.artists import *
from tidalrr.database.albums import *
from tidalrr.database.tracks import *
from tidalrr.database.queues import *
from tidalrr.database.files import *
from tidalrr.database.playlists import *
from pathlib import Path

db_path = Path(__file__).parent.joinpath('config/database.db').absolute()
schema_path = Path(__file__).parent.joinpath('schema.sql').absolute()

def createTables():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    settings = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings';").fetchone()
    conn.close()
    if settings is None:
        connection = sqlite3.connect(db_path)
        with open(schema_path) as f:
            connection.executescript(f.read())
        cur = connection.cursor()
        cur.execute("INSERT INTO settings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                    False,
                    '',
                    '',
                    '',
                    '',
                    '',
                    ''
                    )
                    )
        cur.execute("INSERT INTO tidal_key VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    ('', 
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
                    '',
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
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    settings = conn.execute('SELECT * FROM settings').fetchone()
    conn.close()
    if settings is not None:
        settings = Settings(**settings)
    return settings

def getTidalKey() -> LoginKey:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    key = conn.execute('SELECT * FROM tidal_key').fetchone()
    conn.close()
    if key is not None:
        key = LoginKey(**key)
    return key

def setSettings(settings=Settings):
    connection = sqlite3.connect(db_path)
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
                scanUserPlaylists = ?,\
                lidarrUrl = ?,\
                lidarrApi = ?,\
                tidalToken = ?,\
                plexUrl = ?,\
                plexToken = ?,\
                plexHomePath = ?\
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
                    settings.scanUserPlaylists,
                    settings.lidarrUrl,
                    settings.lidarrApi,
                    settings.tidalToken,
                    settings.plexUrl,
                    settings.plexToken,
                    settings.plexHomePath
                    ))
    connection.commit()
    connection.close()

def setTidalKey(key=LoginKey):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("UPDATE tidal_key SET \
                deviceCode = ?,\
                userCode = ?,\
                verificationUrl = ?,\
                authCheckTimeout = ?,\
                authCheckInterval = ?,\
                userId = ?,\
                countryCode = ?,\
                accessToken = ?,\
                refreshToken = ?,\
                expiresIn = ?,\
                token = ?,\
                clientId = ?,\
                clientSecret = ?\
                ",(
                    key.deviceCode,
                    key.userCode,
                    key.verificationUrl,
                    key.authCheckTimeout,
                    key.authCheckInterval,
                    key.userId,
                    key.countryCode,
                    key.accessToken,
                    key.refreshToken,
                    key.expiresIn,
                    key.token,
                    key.clientId,
                    key.clientSecret
                    ))
    connection.commit()
    connection.close()

def getStats():
    print(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT 'Artists' as type, count(*) as count FROM tidal_artists\
                        UNION\
                        SELECT 'Artists Queued' as type, count(*) as count FROM tidal_artists WHERE queued = TRUE\
                        UNION\
                        SELECT 'Artists Downloaded' as type, count(*) as count FROM tidal_artists WHERE downloaded = TRUE\
                        UNION\
                        SELECT 'Albums' as type, count(*) as count FROM tidal_albums\
                        UNION\
                        SELECT 'Albums Queued' as type, count(*) as count FROM tidal_albums WHERE queued = TRUE\
                        UNION\
                        SELECT 'Albums Downloaded' as type, count(*) as count FROM tidal_albums WHERE downloaded = TRUE\
                        UNION\
                        SELECT 'Tracks' as type, count(*) as count FROM tidal_tracks\
                        UNION\
                        SELECT 'Tracks Queued' as type, count(*) as count FROM tidal_tracks WHERE queued = TRUE\
                        UNION\
                        SELECT 'Tracks Downloaded' as type, count(*) as count FROM tidal_tracks WHERE downloaded = TRUE\
                        UNION\
                        SELECT 'Playlists' as type, count(*) as count FROM tidal_playlists\
                        UNION\
                        SELECT 'Playlists Queued' as type, count(*) as count FROM tidal_playlists WHERE queued = TRUE\
                        UNION\
                        SELECT 'Playlists Downloaded' as type, count(*) as count FROM tidal_playlists WHERE downloaded = TRUE\
                        UNION\
                        SELECT 'Download Queue' as type, count(*) as count FROM tidal_queue\
                        UNION\
                        SELECT 'Downloaded Files' as type, count(*) as count FROM files\
                        "
                        ).fetchall()
    conn.close()
    return rows