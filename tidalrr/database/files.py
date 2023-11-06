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
from pathlib import Path

db_path = Path(__file__).parent.joinpath('config/database.db').absolute()

def addFiles(file=File):
    connection = sqlite3.connect(db_path)
    cur = connection.cursor()
    cur.execute("INSERT OR IGNORE INTO files (description, type, id, path) VALUES (?, ?, ?, ?)",
                (
                    file.description,
                    file.type,
                    file.id,
                    file.path
                ))
    connection.commit()
    connection.close()

def getFiles() -> [File]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM files').fetchall()
    conn.close()
    files =[]
    if len(rows) > 0 :
        for f in rows:
            files.append(convertToFile(f))
    return files

def getFileById(id= int) -> File:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM files WHERE id = ?', (id,)).fetchone()
    conn.close()
    file = None
    if row is not None:
        file = convertToFile(row)
    return file
