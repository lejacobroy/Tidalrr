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
    try:
        covers = getTidalQueues('Cover')
    except Exception as e:
        logger.error("Error getting cover queues: %s", e)
        return
    
    for i, cover in enumerate(covers):
        try:
            file = getFileById(cover.id)

            if file is None:
                try:
                    album = getTidalAlbum(cover.id)
                except Exception as e:
                    logger.error("Error getting album %s: %s", cover.id, e)
                    continue

                # check existing path
                if not exists(cover.path):
                    try:
                        aigpy.net.downloadFile(cover.url, cover.path)
                    except Exception as e:
                        logger.error("Error downloading %s: %s", cover.url, e)
                        continue
                    
                    logger.info("Downloaded album cover %s/%s %s", str(i), str(len(covers)), album.title)
                
                file = File(
                    description=album.title,
                    type='Cover',
                    id=cover.id,
                    path=cover.path
                )
                try:
                    addFiles(file)
                except Exception as e:
                    logger.error("Error adding file %s: %s", file.id, e)
                    continue

            try:
                delTidalQueue(cover.path)
            except Exception as e:
                logger.error("Error deleting queue %s: %s", cover.path, e)

        except Exception as e:
            logger.error("Error processing cover %s: %s", cover.id, e)