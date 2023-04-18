#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2020/11/08
@Author  :   Yaronzz
@Version :   3.0
@Contact :   yaronhuang@foxmail.com
@Desc    :   
'''
import sys
import getopt

from events import *
from settings import *
from lidarr import *
from webserver import *

def mainCommand():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   "holsq:u:f:a:i:", 
                                   ["help", "url", "file", "output", "quality"])
    except getopt.GetoptError as errmsg:
        Printf.err(vars(errmsg)['msg'] + ". Use 'tidalrr -h' for usage.")
        return

    for opt, val in opts:
        if opt in ('-h', '--help'):
            Printf.usage()
            return
        if opt in ('-v', '--version'):
            Printf.logo()
            return
        if opt in ('-u', '--url'):
            use_url(val)
            continue
        if opt in ('-a', '--album'):
            use_text(val)
            continue
        if opt in ('-l', '--lidarr'):
            syncLidarr()
            continue
        if opt in ('-s', '--syncplaylists'):
            syncTidal()
            continue
        if opt in ('-i', '--inject'):
            injectPlaylist(val)
            continue
        if opt in ('-f', '--file'):
            Printf.info('Using file list: '+val)
            file1 = open(val, 'r')
            Lines = file1.readlines()
            count = 0
            # Strips the newline character
            for line in Lines:
                count += 1
                Printf.info("Url #{}: {}".format(count, line.strip()))
                use_url(line.strip())
            continue
        if opt in ('-o', '--output'):
            SETTINGS.downloadPath = val
            SETTINGS.save()
            continue
        if opt in ('-q', '--quality'):
            SETTINGS.audioQuality = SETTINGS.getAudioQuality(val)
            SETTINGS.save()
            continue


def use_url(url):
    start(url)

def use_text(txt):
    Printf.info(LANG.select.SETTING_DOWNLOAD_PATH + ':' + SETTINGS.downloadPath)
    alb = Album()
    alb.title = txt
    start_album_search(alb)

def syncLidarr():
    Printf.info(LANG.select.SETTING_DOWNLOAD_PATH + ':' + SETTINGS.downloadPath)
    albums = [Album()]
    albums = getMissingAlbums(SETTINGS.lidarrURL, SETTINGS.lidarrAPI)
    for a in albums :
        if a.title is not None:    
            # set download path
            SETTINGS.downloadPath = str(a.path)
            start_album_search(a)
    Printf.info('Lidarr wanted list synced, go update it.')

def syncTidal():
    Printf.info(LANG.select.SETTING_DOWNLOAD_PATH + ':' + SETTINGS.downloadPath + ' User: ')
    start_playlist_sync(TOKEN.userid)
    Printf.info('Tidall playlists synced.')

def injectPlaylist(playlistPath):
    # use spark.py function to load the .m3u8 file into Spark DB
    # spark DB is located at '~/Library/Applications Support/Devialet/Spakr/Collection.db'
    Printf.info('Validating m3u8 playlist...')
    # read .m3u8
        # is valid, make a copy of the db with the date
    Printf.success('Valid m3u8, DB backup.')
        # inject the playlist
    Printf.success('Injected playlist X into Spark.')

def startWebserver():
    port = int(os.environ.get("PORT", 8000))
    app = tidalrrWeb()
    app.run(host="0.0.0.0", port=port)

def main():
    SETTINGS.read(getProfilePath())
    TOKEN.read(getTokenPath())
    TIDAL_API.apiKey = apiKey.getItem(SETTINGS.apiKeyIndex)
    
    #Printf.logo()
    #Printf.settings()
    if not aigpy.path.mkdirs(SETTINGS.downloadPath):
        Printf.err(LANG.select.MSG_PATH_ERR + SETTINGS.downloadPath)
        return

    if not apiKey.isItemValid(SETTINGS.apiKeyIndex):
        changeApiKey()
        loginByWeb()
    elif not loginByConfig():
        loginByWeb()

    if len(sys.argv) > 1:
        mainCommand()
    else:
        startWebserver()

if __name__ == '__main__':
    # test()
    main()
