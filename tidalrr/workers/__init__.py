#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   workerStart.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''

from tidalrr.tidal import *

def tidalrrStart():
    createTables()
    settings = getSettings()
    #Printf.logo()
    #Printf.settings()
    if not aigpy.path.mkdirs(settings.downloadPath):
        print(settings.downloadPath)
        return

    """ if not isItemValid(settings.apiKeyIndex):
        changeApiKey()
        loginByWeb()
    elif not loginByConfig():
        loginByWeb() """

def parseContributors(roleType, Contributors):
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
    
def setMetaData(track: Track, album: Album, artist: Artist, artists:str, filepath, contributors, lyrics):
    #artist = getTidalArtist(album.artist)
    #artist = [(getTidalArtist(album.artist).name)]
    obj = aigpy.tag.TagTool(filepath)
    obj.album = album.title
    obj.title = track.title
    if not aigpy.string.isNull(track.version):
        obj.title += ' (' + track.version + ')'

    #obj.artist = artist.name
    obj.artist = artists
    obj.copyright = track.copyRight
    obj.tracknumber = track.trackNumber
    obj.discnumber = track.volumeNumber
    obj.composer = parseContributors('Composer', contributors)
    obj.isrc = track.isrc

    obj.albumartist = artist
    obj.date = album.releaseDate
    obj.totaldisc = album.numberOfVolumes
    obj.lyrics = lyrics
    if obj.totaldisc <= 1:
        obj.totaltrack = album.numberOfTracks
    coverpath = TIDAL_API.getCoverUrl(album.cover)
    obj.save(coverpath)

def isSkip(finalpath, url):
    settings = getSettings()
    if not settings.checkExist:
        return False
    curSize = aigpy.file.getSize(finalpath)
    if curSize <= 0:
        # check if masters version exists
        #print("File dosen't exists.")
        #print("normpath "+os.path.normpath(finalpath))
        #print("splitted "+os.path.normpath(finalpath).split(os.path.sep))
        newPath = os.path.normpath(finalpath).split(os.path.sep)
        #print("second-last "+newPath[-2])
        newPath[-2] = newPath[-2]+" [M]"
        #print(newPath[-2])
        newPath = os.path.join(*newPath)
        #print("/"+os.path.normpath(newPath))
        curSize = aigpy.file.getSize("/"+newPath)
        #print(finalpath+"\n"+Path(*"/".join(map(str, newPath))))
        if curSize <= 0:
            return False
        else:
            #print("File dosen't exists, but there's a Master version available, skipping")
            return True
    netSize = aigpy.net.getSize(url)
    return curSize >= netSize

def scanCover(album):
    cover = getFileById(album.id)
    if cover is None:
        if album is None:
            return
        path = getAlbumPath(album) 
        if path is not None:
            path = path + '/cover.jpg'
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