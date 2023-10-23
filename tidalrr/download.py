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


from concurrent.futures import ThreadPoolExecutor

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


def __encrypted__(stream, srcPath, descPath):
    if aigpy.string.isNull(stream.encryptionKey):
        os.replace(srcPath, descPath)
    else:
        key, nonce = decrypt_security_token(stream.encryptionKey)
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
    artist = getTidalArtist(album.artist)
    obj = aigpy.tag.TagTool(filepath)
    obj.album = album.title
    obj.title = track.title
    if not aigpy.string.isNull(track.version):
        obj.title += ' (' + track.version + ')'

    obj.artist = artist.name
    obj.copyright = track.copyRight
    obj.tracknumber = track.trackNumber
    obj.discnumber = track.volumeNumber
    obj.composer = __parseContributors__('Composer', contributors)
    obj.isrc = track.isrc

    obj.albumartist = artist.name
    obj.date = album.releaseDate
    obj.totaldisc = album.numberOfVolumes
    obj.lyrics = lyrics
    if obj.totaldisc <= 1:
        obj.totaltrack = album.numberOfTracks
    coverpath = TIDAL_API.getCoverUrl(album.cover)
    obj.save(coverpath)


def downloadCover(album):
    if album is None:
        return
    path = getAlbumPath(album) + '/cover.jpg'
    url = TIDAL_API.getCoverUrl(album.cover)

    queue = Queue(
        type='Cover',
        login=False,
        id=album.id,
        path=path,
        url=url,
        encryptionKey=''
    )

    addTidalQueue(queue)
    #aigpy.net.downloadFile(url, path)


def downloadAlbumInfo(album:Album, tracks: [Track]):
    if album is None:
        return

    path = getAlbumPath(album)
    aigpy.path.mkdirs(path)

    path += '/AlbumInfo.txt'
    infos = ""
    infos += "[ID]          %s\n" % (str(album.id))
    infos += "[Title]       %s\n" % (str(album.title))
    infos += "[Artists]     %s\n" % (getArtistsName(album.artists))
    infos += "[ReleaseDate] %s\n" % (str(album.releaseDate))
    infos += "[SongNum]     %s\n" % (str(album.numberOfTracks))
    infos += "[Duration]    %s\n" % (str(album.duration))
    infos += '\n'

    for index in range(0, album.numberOfVolumes):
        volumeNumber = index + 1
        infos += f"===========CD {volumeNumber}=============\n"
        for item in tracks:
            if item.volumeNumber != volumeNumber:
                continue
            infos += '{:<8}'.format("[%d]" % item.trackNumber)
            infos += "%s\n" % item.title
    aigpy.file.write(path, infos, "w+")

def getDownloadTrackFilename(track: Track, playlist: Playlist):
    stream = TIDAL_API.getStreamUrl(track.id, SETTINGS.audioQuality)
    path = getTrackPath(track, stream, None, playlist, 'filename')
    return path


def downloadTrack(track: Track, album=None, playlist=None, userProgress=None, partSize=1048576):
    #try:
    print('downloadTrack')
    stream = TIDAL_API.getStreamUrl(track.id, SETTINGS.audioQuality)
    artist = getTidalArtist(track.artist)
    album = getTidalAlbum(track.album)

    path = getTrackPath(track, stream, artist, album, playlist)
    print(path)
    #if SETTINGS.showTrackInfo and not SETTINGS.multiThread:
    #    Printf.track(track, stream)
    print(track.title)
    #if userProgress is not None:
    #    userProgress.updateStream(stream)

    number = 0
    if track.trackNumberOnPlaylist:
        number = track.trackNumberOnPlaylist
    else:
        number = track.trackNumber
    print(number)
    # check exist
    if __isSkip__(path, stream.url):
        Printf.info(str(number)+ " : " + artist.name + " - " + album.title + " - " + track.title + " (skip:already exists!)")
        return True, path

    # download
    logging.info("[DL Track] name=" + aigpy.path.getFileName(path) + "\nurl=" + stream.url)
    if SETTINGS.downloadDelay:
        sleep_time = random.randint(500, 5000) / 1000
        #print(f"Sleeping for {sleep_time} seconds, to mimic human behaviour and prevent too many requests error")
        #time.sleep(sleep_time)

    queue = Queue(
        type='Track',
        login=True,
        id=track.id,
        path=path,
        url=stream.url,
        encryptionKey=stream.encryptionKey
    )

    addTidalQueue(queue)
    print('queue')
    #tool = aigpy.download.DownloadTool(path + '.part', stream.urls)
    #tool.setUserProgress(userProgress)
    #tool.setPartSize(partSize)
    #check, err = tool.start(SETTINGS.showProgress and not SETTINGS.multiThread)
    #if not check:
    #    Printf.err(f"DL Track[{track.title}] failed.{str(err)}")
    #    return False, str(err)

    # encrypted -> decrypt and remove encrypted file
    #__encrypted__(stream, path + '.part', path)

    # contributors
    try:
        contributors = TIDAL_API.getTrackContributors(track.id)
    except:
        contributors = None
    print('testcontrib')
    # lyrics
    try:
        lyrics = TIDAL_API.getLyrics(track.id).subtitles
        if SETTINGS.lyricFile:
            lrcPath = path.rsplit(".", 1)[0] + '.lrc'
            aigpy.file.write(lrcPath, lyrics, 'w')
    except:
        lyrics = ''

    __setMetaData__(track, album, path, contributors, lyrics)
    
    Printf.success(str(number)+ " : " + artist.name + " - " + album.title + " - " + track.title)
    #Printf.info(str(number)+ " : " +aigpy.path.getFileName(path) + " (skip:already exists!)")
    return True, path
    #except Exception as e:
    #    Printf.err(f"DL Track[{track.title}] failed.{str(e)}")
    #    return False, str(e)


def downloadTracks(tracks, album: Album = None, playlist : Playlist=None):
    print('downloadTracks')
    def __getAlbum__(item: Track):
        album = TIDAL_API.getAlbum(item.album.id)
        if SETTINGS.saveCovers and not SETTINGS.usePlaylistFolder:
            downloadCover(album)
            print('downloadCover')
        return album
    paths = []
    if not SETTINGS.multiThread:
        for index, item in enumerate(tracks):
            itemAlbum = album
            if itemAlbum is None:
                itemAlbum = __getAlbum__(item)
                item.trackNumberOnPlaylist = index + 1
            paths.append(downloadTrack(item, itemAlbum, playlist)[1])
    else:
        thread_pool = ThreadPoolExecutor(max_workers=5)
        for index, item in enumerate(tracks):
            itemAlbum = album
            if itemAlbum is None:
                itemAlbum = __getAlbum__(item)
            item.trackNumberOnPlaylist = index + 1
            thread_pool.submit(downloadTrack, item, itemAlbum, playlist)
        thread_pool.shutdown(wait=True)
    return paths

def downloadPlaylistInfos(tracks, album: Album = None, playlist : Playlist=None):
    def __getAlbum__(item: Track):
        album = TIDAL_API.getAlbum(item.album.id)
        if SETTINGS.saveCovers and not SETTINGS.usePlaylistFolder:
            downloadCover(album)
        return album
    
    if not SETTINGS.multiThread:
        for index, item in enumerate(tracks):
            itemAlbum = album
            if itemAlbum is None:
                itemAlbum = __getAlbum__(item)
                item.trackNumberOnPlaylist = index + 1
            downloadTrack(item, itemAlbum, playlist)
    else:
        thread_pool = ThreadPoolExecutor(max_workers=5)
        for index, item in enumerate(tracks):
            itemAlbum = album
            if itemAlbum is None:
                itemAlbum = __getAlbum__(item)
                item.trackNumberOnPlaylist = index + 1
            thread_pool.submit(downloadTrack, item, itemAlbum, playlist)
        thread_pool.shutdown(wait=True)
