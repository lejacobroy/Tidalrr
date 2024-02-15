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
from tidalrr.database.artists import *
from tidalrr.database.albums import *
from tidalrr.database.tracks import *
from tidalrr.database.queues import *
from tidalrr.database.files import *
from tidalrr.database.playlists import *
from pathlib import Path

db_path = Path(__file__).parent.joinpath('config/database.db').absolute()
schema_path = Path(__file__).parent.joinpath('schema.sql').absolute()
housekeeping_path = Path(__file__).parent.joinpath('housekeeping.sql').absolute()

def migration():
    conn = sqlite3.connect(db_path)
    version = 0
    try:
         # Get current version
        cur = conn.execute("SELECT version FROM settings;")
        version = cur.fetchone()[0]
    except:
        version = 0

    if version == 0:
        # Upgrade to v1
        conn.execute("ALTER TABLE settings \
                     ADD COLUMN version integer;")
        conn.execute("ALTER TABLE settings \
                    ADD COLUMN scansStartHour INTEGER;")
        conn.execute("ALTER TABLE settings \
                    ADD COLUMN scansDuration INTEGER;")
        conn.execute("ALTER TABLE settings \
                    ADD COLUMN downloadsStartHour INTEGER;")
        conn.execute("ALTER TABLE settings \
                    ADD COLUMN downloadsDuration INTEGER;") 
        conn.execute("update settings set version = 1, scansStartHour = 23, scansDuration = 4, downloadsStartHour = 3, downloadsDuration = 9;")

    if version == 1:
        conn.execute("ALTER TABLE tidal_artists \
                    RENAME COLUMN queued TO monitored;")
        conn.execute("ALTER TABLE tidal_albums \
                    RENAME COLUMN queued TO monitored;")
        conn.execute("ALTER TABLE tidal_playlists \
                    RENAME COLUMN queued TO monitored;")
        conn.execute("update settings set version = 2")

    if version == 2:
        # convert the queues to queued tracks
        conn.execute("UPDATE tidal_tracks SET queued = 1 WHERE id IN (SELECT id from tidal_queue WHERE type = 'Track');")
        conn.execute("DELETE FROM tidal_queue WHERE type = 'Track' AND id in (SELECT id from tidal_tracks WHERE queued = 1);")
        conn.execute("update settings set version = 3")
    conn.commit()
    conn.close()

def createTables():
    # checking if the directory config  
    # exist or not. 
    
    if not os.path.exists(Path(__file__).parent.joinpath('config/').absolute()): 
        # if the demo_folder directory is not present  
        # then create it. 
        os.makedirs(Path(__file__).parent.joinpath('config/').absolute()) 
        
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    settings = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings';").fetchone()
    if settings is None:
        with open(schema_path) as f:
            conn.executescript(f.read())
        cur = conn.cursor()
        cur.execute("INSERT INTO settings (albumFolderFormat, apiKeyindex, audioQuality, checkExist, downloadDelay, downloadPath, includeEP, language, lyricFile, multiThread,\
                    playlistFolderFormat, saveAlbumInfo, saveCovers, showProgress, showTrackInfo, TrackFileFormat, usePlaylistFolder, scanUserPlaylists, lidarrUrl, lidarrApi, \
                    tidalToken, plexUrl, plexToken, plexHomePath, version, scansStartHour, scansDuration, downloadsStartHour, downloadsDuration) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?)",
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
                    '',
                    4,
                    23,
                    4,
                    3,
                    9
                    )
                    )
        cur.execute("INSERT INTO tidal_key (deviceCode,\
                userCode, verificationUrl, authCheckTimeout ,authCheckInterval , userId, countryCode, accessToken,\
                refreshToken, expiresIn, token, clientId, clientSecret) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
        conn.commit()
    conn.close()

def housekeeping():
    migration()
    conn = sqlite3.connect(db_path)
    with open(housekeeping_path) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    # update downloaded albums & artists
    updateTidalAlbumsDownloaded()
    updateTidalArtistsDownloaded()
    updateTidalPlaylistsDownloaded()

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
                plexHomePath = ?,\
                version = ?,\
                scansStartHour = ?,\
                scansDuration = ?,\
                downloadsStartHour = ?,\
                downloadsDuration = ?\
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
                    settings.plexHomePath,
                    settings.version,
                    settings.scansStartHour,
                    settings.scansDuration,
                    settings.downloadsStartHour,
                    settings.downloadsDuration
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
                        SELECT 'Artists monitored' as type, count(*) as count FROM tidal_artists WHERE monitored = TRUE\
                        UNION\
                        SELECT 'Artists Downloaded' as type, count(*) as count FROM tidal_artists WHERE downloaded = TRUE\
                        UNION\
                        SELECT 'Albums' as type, count(*) as count FROM tidal_albums\
                        UNION\
                        SELECT 'Albums monitored' as type, count(*) as count FROM tidal_albums WHERE monitored = TRUE\
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
                        SELECT 'Playlists monitored' as type, count(*) as count FROM tidal_playlists WHERE monitored = TRUE\
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
