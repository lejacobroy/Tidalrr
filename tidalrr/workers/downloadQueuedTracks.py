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

from tidalrr.paths import *
from tidalrr.decryption import *
from tidalrr.tidal import *
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

def workDownloadTrack(queue = Queue, track=Track, partSize=1048576):
    album = getTidalAlbum(track.album)
    
    if not queue.login and isNeedRefresh(queue.url) and queue.type == 'Track':
        print('Refreshing URL '+ track.title)
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
        #logging.info("[DL Track] name=" + aigpy.path.getFileName(queue.path) + "\nurl=" + queue.url)
        if SETTINGS.downloadDelay:
            sleep_time = random.randint(500, 5000) / 1000
            #print(f"Sleeping for {sleep_time} seconds, to mimic human behaviour and prevent too many requests error")
            time.sleep(sleep_time)

        tool = aigpy.download.DownloadTool(queue.path + '.part', [queue.url])
        tool.setPartSize(partSize)
        check, err = tool.start(False,1)
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
        metadataArtists = [album.artists]
        setMetaData(track, album, metadataArtist, metadataArtists, queue.path, contributors, lyrics)
        
        #print(str(number)+ " : " + artist.name + " - " + album.title + " - " + track.title)
        #print(str(number)+ " : " +aigpy.path.getFileName(path) + " (skip:already exists!)")

    # save file in db
    file = File(
        description=track.title,
        type='Track',
        id=track.id,
        path=queue.path
    )
    addFiles(file)


def downloadQueuedTracks():
    tidalrrStart()
    queue_items = getTidalQueues('Track')
    for i, queue in enumerate(queue_items):
        file = getFileById(queue.id)
        if file is None:
            track = getTidalTrack(queue.id)
            print('Downloading track file '+str(i)+'/'+str(len(queue_items))+' '+queue.title)
            workDownloadTrack(queue, track)
        # remove queue in db
        delTidalQueue(queue.path)
        return True