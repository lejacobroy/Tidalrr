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

import multiprocessing
import subprocess
import shlex
import os
from time import gmtime, strftime
from tidalrr.database import *
from tidalrr.workers import print_elapsed_time,tidalrrStart

@print_elapsed_time
def startImportPlex():
    settings = getSettings()
    if settings.plexToken != '' and settings.plexUrl != '':
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" startImportPlex")
        tidalrrStart()
        print('tidalrrStart')
        playlists = getTidalPlaylistDownloaded()
        for i, playlist in enumerate(playlists):
            if hasattr(playlist, 'uuid'):
                # playlist has all tracks downloaded, importing to plex
                command = shlex.split("python3 PPI/main.py --token "+settings.plexToken+" --plex_url "+settings.plexUrl+" '"+os.path.join(playlist.path+'.m3u')+"'")
                subprocess.call(command)

def forkImportPlex():
    # Start foo as a process
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" Starting startImportPlex")
    p = multiprocessing.Process(target=startImportPlex)
    p.start()

    p.join()

    # If thread is active
    if p.is_alive():
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" ImportPlex are running... let's kill it...")
        # Terminate foo
        p.terminate()
        # Cleanup
        p.join()

if __name__ == '__main__':
    forkImportPlex()
    #main()
    #mainSchedule()