
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   download.py
@Time    :   2020/11/08
@Author  :   Yaronzz
@Version :   1.0
@Contact :   yaronhuang@foxmail.com
@Desc    :   
'''
import aigpy
import logging

from paths import *
from printf import *
from decryption import *
from tidal import *
from download import *
from urllib.parse import urlparse
from urllib.parse import parse_qs
import time



def __isSkip__(finalpath, url):
    if not SETTINGS.checkExist:
        return False
    curSize = aigpy.file.getSize(finalpath)
    if curSize <= 0:
        # check if masters version exists
        #Printf.info("File dosen't exists.")
        #Printf.info("normpath "+os.path.normpath(finalpath))
        #Printf.info("splitted "+os.path.normpath(finalpath).split(os.path.sep))
        newPath = os.path.normpath(finalpath).split(os.path.sep)
        #Printf.info("second-last "+newPath[-2])
        newPath[-2] = newPath[-2]+" [M]"
        #Printf.info(newPath[-2])
        newPath = os.path.join(*newPath)
        #Printf.info("/"+os.path.normpath(newPath))
        curSize = aigpy.file.getSize("/"+newPath)
        #Printf.info(finalpath+"\n"+Path(*"/".join(map(str, newPath))))
        if curSize <= 0:
            return False
        else:
            #Printf.info("File dosen't exists, but there's a Master version available, skipping")
            return True
    netSize = aigpy.net.getSize(url)
    return curSize >= netSize


def __encrypted__(encryptionKey, srcPath, descPath):
    if encryptionKey == '':
        os.replace(srcPath, descPath)
    else:
        key, nonce = decrypt_security_token(encryptionKey)
        decrypt_file(srcPath, descPath, key, nonce)
        os.remove(srcPath)


def __parseContributors__(roleType, Contributors):
    if Contributors is None:
        return None
    try:
        ret = []
        for item in Contributors['items']:
            if item['role'] == roleType:
                ret.append(item['name'])
        return ret
    except:
        return None


def __setMetaData__(track: Track, album: Album, filepath, contributors, lyrics):
    obj = aigpy.tag.TagTool(filepath)
    artist = [(getTidalArtist(album.artist).name)]
    obj.album = album.title
    obj.title = track.title
    if not aigpy.string.isNull(track.version):
        obj.title += ' (' + track.version + ')'

    obj.artist = [getArtistsName(json.loads(album.artists))]
    obj.copyright = track.copyRight
    obj.tracknumber = track.trackNumber
    obj.discnumber = track.volumeNumber
    obj.composer = __parseContributors__('Composer', contributors)
    obj.isrc = track.isrc

    obj.albumartist = artist
    obj.date = album.releaseDate
    obj.totaldisc = album.numberOfVolumes
    obj.lyrics = lyrics
    if obj.totaldisc <= 1:
        obj.totaltrack = album.numberOfTracks
    coverpath = TIDAL_API.getCoverUrl(album.cover)
    obj.save(coverpath)
    print(obj.artist)

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
    if not __isSkip__(queue.path, queue.url):
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
            Printf.err(f"DL Track[{track.title}] failed.{str(err)}")
            return False, str(err)

        # encrypted -> decrypt and remove encrypted file
        __encrypted__(queue.encryptionKey, queue.path + '.part', queue.path)

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

    __setMetaData__(track, album, queue.path, contributors, lyrics)
    
    Printf.success(str(number)+ " : " + artist.name + " - " + album.title + " - " + track.title)
    #Printf.info(str(number)+ " : " +aigpy.path.getFileName(path) + " (skip:already exists!)")

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
    return True, queue.path

    
queue_items = getTidalQueues('Track')
for i, queue in enumerate(queue_items):
    workDownloadTrack(queue)