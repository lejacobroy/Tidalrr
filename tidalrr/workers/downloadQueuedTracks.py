#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   workerDownload.py
@Time    :   2023/10/23
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import aigpy
import logging
import time

from paths import *
from decryption import *
from tidal import *
from downloadUtils import *
from urllib.parse import urlparse
from urllib.parse import parse_qs
from tidalrr.workers import *

def refreshStreamURL(id=int):
    return (TIDAL_API.getStreamUrl(id, SETTINGS.audioQuality)).url

def isNeedRefresh(url):
    #extract the 'expire' key from the url
    parsed_url = urlparse(url)
    captured_value = parse_qs(parsed_url.query)['Expires'][0]
    if captured_value > int( time.time() ):
        return False
    return True

def workDownloadTrack(queue = Queue, partSize=1048576):
    track = getTidalTrack(queue.id)
    print(track)
    artist = getTidalArtist(track.artist)
    album = getTidalAlbum(track.album)
    
    if not queue.login and isNeedRefresh(queue.url) and queue.type == 'Track':
        temp = refreshStreamURL(queue.id)
        queue.url = temp.url
        queue.encryptionKey = temp.encryptionKey

    number = 0
    if track.trackNumberOnPlaylist:
        number = track.trackNumberOnPlaylist
    else:
        number = track.trackNumber

    # check exist
    if not isSkip(queue.path, queue.url):
         # download
        logging.info("[DL Track] name=" + aigpy.path.getFileName(queue.path) + "\nurl=" + queue.url)
        if SETTINGS.downloadDelay:
            sleep_time = random.randint(500, 5000) / 1000
            #print(f"Sleeping for {sleep_time} seconds, to mimic human behaviour and prevent too many requests error")
            time.sleep(sleep_time)

        tool = aigpy.download.DownloadTool(queue.path + '.part', [queue.url])
        tool.setPartSize(partSize)
        check, err = tool.start(SETTINGS.showProgress and not SETTINGS.multiThread)
        if not check:
            print(f"DL Track[{track.title}] failed.{str(err)}")
            return False, str(err)

        # encrypted -> decrypt and remove encrypted file
        encrypted(queue.encryptionKey, queue.path + '.part', queue.path)

    # contributors
    try:
        contributors = TIDAL_API.getTrackContributors(track.id)
    except:
        contributors = None

    # lyrics
    try:
        lyrics = TIDAL_API.getLyrics(track.id).subtitles
        if SETTINGS.lyricFile:
            lrcPath = queue.path.rsplit(".", 1)[0] + '.lrc'
            aigpy.file.write(lrcPath, lyrics, 'w')
    except:
        lyrics = ''
    metadataArtist = [(getTidalArtist(album.artist).name)]
    metadataArtists = [getArtistsName(json.loads(album.artists))]
    setMetaData(track, album, metadataArtist, metadataArtists, queue.path, contributors, lyrics)
    
    print(str(number)+ " : " + artist.name + " - " + album.title + " - " + track.title)
    #print(str(number)+ " : " +aigpy.path.getFileName(path) + " (skip:already exists!)")

    # save file in db
    file = File(
        description=track.title,
        type='Track',
        id=track.id,
        path=queue.path
    )
    addFiles(file)

    # remove queue in db
    delTidalQueue(queue.path)
    return True

def downloadQueuedTracks():
    tidalrrStart()
    queue_items = getTidalQueues('Track')
    for i, queue in enumerate(queue_items):
        workDownloadTrack(queue)