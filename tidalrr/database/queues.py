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
import json

database_path = os.path.abspath(os.path.dirname(__file__))+'/../config/database.db'
schema_path = os.path.abspath(os.path.dirname(__file__))+'/schema.sql'

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
    if len(rows) > 0:
        for q in rows:
            queues.append(convertToQueue(q))
    return queues

def getTidalQueueById(id= int) -> Queue:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM tidal_queue WHERE id = ?', (id,)).fetchone()
    conn.close()
    queue = None
    if row is not None:
        queue = convertToQueue(row)
    return queue

def delTidalQueue(path=str):
    conn = sqlite3.connect(database_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM tidal_queue WHERE path = ?', (path,))
    conn.commit()
    conn.close()