#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   downloadQueudOthers.py
@Time    :   2023/10/25
@Author  :   JAcob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import aigpy
from os.path import exists
from tidalrr.paths import *
from tidalrr.decryption import *
from tidalrr.tidal import *
from tidalrr.workers import *

import logging

logger = logging.getLogger(__name__)

def downloadQueuedCovers():
    covers = getTidalQueues('Cover')
    print(len(covers))
    for i, cover in enumerate(covers):
        try:
            file = getFileById(cover.id)

            if file is None:
                try:
                    album = getTidalAlbum(cover.id)
                except Exception as e:
                    print("Error getting album : ", cover.id, e)
                    continue

                # check existing path
                if not exists(cover.path):
                    try:
                        aigpy.net.downloadFile(cover.url, cover.path)
                    except Exception as e:
                        print("Error downloading : ", cover.url, e)
                        continue
                else:
                    delTidalQueue(cover.id)
                
                file = File(
                    description=album.title,
                    type='Cover',
                    id=cover.id,
                    path=cover.path
                )
                try:
                    addFiles(file)
                    delTidalQueue(cover.id)
                    print("Downloaded album cover / ", str(i), str(len(covers)), album.title)
                except Exception as e:
                    print("Error adding file : ", file.id, e)
                    continue
            else:
                delTidalQueue(cover.id)
        except Exception as e:
            print("Error processing cover : ", cover.id, e)