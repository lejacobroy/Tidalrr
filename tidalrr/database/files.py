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

database_path = os.path.abspath(os.path.dirname(__file__))+'/../config/database.db'
schema_path = os.path.abspath(os.path.dirname(__file__))+'/schema.sql'

def convertToFile(file) -> File:
    fileType = File(
        id= file['id'],
        type= file['type'],
        path= file['path'],
        description= file['description']
    )
    return fileType

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
    files =[]
    if len(rows) > 0 :
        for f in rows:
            files.append(convertToFile(f))
    return files

def getFileById(id= int) -> File:
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM files WHERE id = ?', (id,)).fetchone()
    conn.close()
    file = None
    if row is not None:
        file = convertToFile(row)
    return file
