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
import json
from tidalrr.model import *
from pathlib import Path

db_path = Path(__file__).parent.joinpath('config/database.db').absolute()

def addTidalQueue(queue=Queue):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO tidal_queue (url, type, login, id, path, encryptionKey, urls) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    queue.url,
                    queue.type,
                    queue.login,
                    queue.id,
                    queue.path,
                    queue.encryptionKey,
                    json.dumps(queue.urls)
                ))
    connection.commit()
    connection.close()

def getTidalQueues(type=str) -> [Queue]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if type == '':
        rows = conn.execute('SELECT * FROM tidal_queue').fetchall()
    elif type == 'Track':
        rows = conn.execute('SELECT tidal_queue.* FROM tidal_queue \
                            inner join tidal_tracks on tidal_tracks.id = tidal_queue.id\
                            inner join tidal_albums on tidal_albums.id = tidal_tracks.album\
                            inner join tidal_artists on tidal_artists.id = tidal_albums.artist\
                            WHERE tidal_queue.id IS NOT NULL AND tidal_queue.type = "Track" \
                            ORDER BY tidal_artists.name, tidal_albums.title, tidal_tracks.volumeNumber, tidal_tracks.trackNumber').fetchall()
    elif type == 'Cover':
        rows = conn.execute('SELECT tidal_queue.* FROM tidal_queue \
                            inner join tidal_albums on tidal_albums.id = tidal_queue.id\
                            inner join tidal_artists on tidal_artists.id = tidal_albums.artist\
                            WHERE tidal_queue.id IS NOT NULL AND tidal_queue.type = "Cover" \
                            ORDER BY tidal_artists.name, tidal_albums.title').fetchall()
    conn.close()
    queues = []
    if len(rows) > 0:
        for q in rows:
            queues.append(convertToQueue(q))
    return queues

def getTidalQueueById(id= int) -> Queue:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM tidal_queue WHERE id = ?', (id,)).fetchone()
    conn.close()
    queue = None
    if row is not None:
        queue = convertToQueue(row)
    return queue

def delTidalQueue(id=str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM tidal_queue WHERE id = ?', (id,))
    conn.commit()
    conn.close()