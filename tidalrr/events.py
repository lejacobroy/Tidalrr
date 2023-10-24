#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  events.py
@Date    :  2022/06/10
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""

import aigpy
import time

from tidalrr.model import *
from tidalrr.tidal import *
from tidalrr.apiKey import *
from tidalrr.paths import *

'''
=================================
START DOWNLOAD
=================================
'''



""" def start_playlist_sync(UserId=None):
    playlists = TIDAL_API.getPlaylistsAndFavorites(UserId)
    for playlist in playlists:
        if playlist.title is not None:
            start_type(Type.Playlist, playlist) """


""" def start_playlist(obj: Playlist):
    print(obj)
    # here we have the playlist object, we can export it to json
    #print(aigpy.model.modelToDict(obj))
    # save this to playlist.json
    data = aigpy.model.modelToDict(obj)

    path = getPlaylistPath(obj)

    aigpy.file.write(str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.json', json.dumps(data), 'w+')

    print('Saved playlist json info to : '+str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.json')

    tracks = TIDAL_API.getItems(obj.uuid, Type.Playlist)
    paths = downloadTracks(tracks, None, obj)

    with open(str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u', 'w') as f:
        #f.write('#EXTM3U\n')
        for i,item in enumerate(paths, start=1):
            f.write(str(getTrueHomePath())+'/'+item+'\n')
    print('Done generating m3u playlist file: '+str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u')

    # Generate the playlist file
    with open(str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u8', 'w') as f:
        f.write('#EXTM3U\n')
        for i,item in enumerate(aigpy.model.modelListToDictList(tracks), start=1):
            track = Track(*item)
            track.trackNumberOnPlaylist = i
            filename = path[i-1]
            f.write(f'#EXTINF:{item["duration"]},{item["artist"]["name"]} - {item["title"]}\n')
            f.write(str(getTrueHomePath())+'/'+filename+'\n') 
    print('Done generating m3u8 playlist file: '+str(getTrueHomePath())+'/config/Playlists/'+obj.title+'.m3u8')

def start_mix(obj: Mix):
    print(obj)
    downloadTracks(obj.tracks, None, None) """

""" 
def start_file(string):
    txt = aigpy.file.getContent(string)
    if aigpy.string.isNull(txt):
        print("Nothing can read!")
        return
    array = txt.split('\n')
    for item in array:
        if aigpy.string.isNull(item):
            continue
        if item[0] == '#':
            continue
        if item[0] == '[':
            continue
        start(item)


def start_type(etype: Type, obj):
    print('start_type', etype)
    if etype == Type.Artist:
        addTidalArtist(obj)
        start_artist(obj)
    elif etype == Type.Track:
        addTidalTrack(Track(*obj))
        start_track(Track(*obj))
    elif etype == Type.Album:
        addTidalAlbum(obj)
        start_album(obj)
    elif etype == Type.Playlist:
        addTidalPlaylist(obj)
        start_playlist(obj)
    elif etype == Type.Mix:
        start_mix(obj)


def start(string):
    print('start')
    if aigpy.string.isNull(string):
        print('Please enter something.')
        return

    strings = string.split(" ")
    for item in strings:
        if aigpy.string.isNull(item):
            continue
        if os.path.exists(item):
            start_file(item)
            return
        try:
            etype, obj = TIDAL_API.getByString(item)
        except Exception as e:
            print(str(e) + " [" + item + "]")
            return

        try:
            start_type(etype, obj)
        except Exception as e:
            print(str(e))
 """

'''
=================================
CHANGE SETTINGS
=================================
'''


def changeApiKey():
    item = getItem(SETTINGS.apiKeyIndex)
    ver = getVersion()

    print(f'Current APIKeys: {str(SETTINGS.apiKeyIndex)} {item["platform"]}-{item["formats"]}')
    print(f'Current Version: {str(ver)}')
    print(getItems())
    index = int(print("APIKEY index:",getLimitIndexs()))

    if index != SETTINGS.apiKeyIndex:
        SETTINGS.apiKeyIndex = index
        SETTINGS.save()
        TIDAL_API.apiKey = getItem(index)
        return True
    return False


'''
=================================
LOGIN
=================================
'''


def __displayTime__(seconds, granularity=2):
    if seconds <= 0:
        return "unknown"

    result = []
    intervals = (
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1),
    )

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


def loginByWeb():
    try:
        #print(LANG.select.AUTH_START_LOGIN)
        # get device code
        url = TIDAL_API.getDeviceCode()

        """ print(LANG.select.AUTH_NEXT_STEP.format(
            aigpy.cmd.green(url),
            aigpy.cmd.yellow(__displayTime__(TIDAL_API.key.authCheckTimeout))))
        print(LANG.select.AUTH_WAITING) """

        start = time.time()
        elapsed = 0
        while elapsed < TIDAL_API.key.authCheckTimeout:
            elapsed = time.time() - start
            if not TIDAL_API.checkAuthStatus():
                time.sleep(TIDAL_API.key.authCheckInterval + 1)
                continue

            """ print(LANG.select.MSG_VALID_ACCESSTOKEN.format(
                __displayTime__(int(TIDAL_API.key.expiresIn)))) """

            TOKEN.userid = TIDAL_API.key.userId
            TOKEN.countryCode = TIDAL_API.key.countryCode
            TOKEN.accessToken = TIDAL_API.key.accessToken
            TOKEN.refreshToken = TIDAL_API.key.refreshToken
            TOKEN.expiresAfter = time.time() + int(TIDAL_API.key.expiresIn)
            TOKEN.save()
            return True

        raise Exception()
    except Exception as e:
        print(f"Login failed.{str(e)}")
        return False


def loginByConfig():
    try:
        if aigpy.string.isNull(TOKEN.accessToken):
            return False

        if TIDAL_API.verifyAccessToken(TOKEN.accessToken):
            """ print(LANG.select.MSG_VALID_ACCESSTOKEN.format(
                __displayTime__(int(TOKEN.expiresAfter - time.time())))) """

            TIDAL_API.key.countryCode = TOKEN.countryCode
            TIDAL_API.key.userId = TOKEN.userid
            TIDAL_API.key.accessToken = TOKEN.accessToken
            return True

        #print(LANG.select.MSG_INVALID_ACCESSTOKEN)
        if TIDAL_API.refreshAccessToken(TOKEN.refreshToken):
            """ print(LANG.select.MSG_VALID_ACCESSTOKEN.format(
                __displayTime__(int(TIDAL_API.key.expiresIn)))) """

            TOKEN.userid = TIDAL_API.key.userId
            TOKEN.countryCode = TIDAL_API.key.countryCode
            TOKEN.accessToken = TIDAL_API.key.accessToken
            TOKEN.expiresAfter = time.time() + int(TIDAL_API.key.expiresIn)
            TOKEN.save()
            return True
        else:
            TokenSettings().save()
            return False
    except Exception as e:
        return False


def loginByAccessToken():
    try:
        print("-------------AccessToken---------------")
        token = print("accessToken('0' go back):")
        if token == '0':
            return
        TIDAL_API.loginByAccessToken(token, TOKEN.userid)
    except Exception as e:
        print(str(e))
        return

    print("-------------RefreshToken---------------")
    refreshToken = print("refreshToken('0' to skip):")
    if refreshToken == '0':
        refreshToken = TOKEN.refreshToken

    TOKEN.accessToken = token
    TOKEN.refreshToken = refreshToken
    TOKEN.expiresAfter = 0
    TOKEN.countryCode = TIDAL_API.key.countryCode
    TOKEN.save()
