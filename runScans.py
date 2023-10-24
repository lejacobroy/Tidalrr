#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   runScans.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''

from tidalrr.workers.scanQueuedArtists import *
from tidalrr.workers.scanQueuedAlbums import *
from tidalrr.workers.scanQueuedTracks import *

def main():
    scanQueuedArtists()
    scanQueuedAlbums()
    scanQueuedTracks()

main()