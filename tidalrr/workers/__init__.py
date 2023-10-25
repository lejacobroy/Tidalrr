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
from tidalrr.settings import *
from tidalrr.tidal import *

def tidalrrStart():
    #createTables()
    SETTINGS.read()
    TOKEN.read()
    TIDAL_API.apiKey = getItem(SETTINGS.apiKeyIndex)
    
    #Printf.logo()
    #Printf.settings()
    if not aigpy.path.mkdirs(SETTINGS.downloadPath):
        print(SETTINGS.downloadPath)
        return

    if not isItemValid(SETTINGS.apiKeyIndex):
        changeApiKey()
        loginByWeb()
    elif not loginByConfig():
        loginByWeb()

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

    obj.albumartist = artist.name
    obj.date = album.releaseDate
    obj.totaldisc = album.numberOfVolumes
    obj.lyrics = lyrics
    if obj.totaldisc <= 1:
        obj.totaltrack = album.numberOfTracks
    coverpath = TIDAL_API.getCoverUrl(album.cover)
    obj.save(coverpath)

def isSkip(finalpath, url):
    if not SETTINGS.checkExist:
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