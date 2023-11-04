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
    cur.execute("INSERT OR IGNORE INTO tidal_queue VALUES (?, ?, ?, ?, ?, ?, ?)",
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
    else:
        rows = conn.execute('SELECT * FROM tidal_queue WHERE type = ?', (type,)).fetchall()
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

def delTidalQueue(path=str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM tidal_queue WHERE path = ?', (path,))
    conn.commit()
    conn.close()