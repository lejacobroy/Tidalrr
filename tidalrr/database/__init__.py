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