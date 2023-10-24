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

database_path = os.path.abspath(os.path.dirname(__file__))+'/database.db'
schema_path = os.path.abspath(os.path.dirname(__file__))+'/schema.sql'

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