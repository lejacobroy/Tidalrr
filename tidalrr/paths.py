#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  paths.py
@Date    :  2022/06/10
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""
import os
import aigpy
import datetime

from tidal import *
from settings import *

def __fixPath__(name: str):
    return aigpy.path.replaceLimitChar(name, '-').strip()


def __getYear__(releaseDate: str):
    if releaseDate is None or releaseDate == '':
        return ''
    return aigpy.string.getSubOnlyEnd(releaseDate, '-')


def __getDurationStr__(seconds):
    time_string = str(datetime.timedelta(seconds=seconds))
    if time_string.startswith('0:'):
        time_string = time_string[2:]
    return time_string


def __getExtension__(stream: StreamUrl):
    if '.flac' in stream.url:
        return '.flac'
    if '.mp4' in stream.url:
        if 'ac4' in stream.codec or 'mha1' in stream.codec:
            return '.mp4'
        elif 'flac' in stream.codec:
            return '.flac'
        return '.m4a'
    return '.m4a'


def getAlbumPath(album):
    print('album', album)
    artistName = __fixPath__(getArtistsName(album.artists))
    print('artistName',artistName)
    albumArtistName = __fixPath__(getTidalArtist(album.artist).name) if album.artist is not None else ""
    print('albumArtistName',albumArtistName)
    # album folder pre: [ME]
    flag = TIDAL_API.getFlag(album, Type.Album, True, "")
    if SETTINGS.audioQuality != AudioQuality.Master and SETTINGS.audioQuality != AudioQuality.Max:
        flag = flag.replace("M", "")
    if flag != "":
        flag = "[" + flag + "] "

    # album and addyear
    albumName = __fixPath__(album.title)
    year = __getYear__(album.releaseDate)

    # retpath
    retpath = SETTINGS.albumFolderFormat
    if retpath is None or len(retpath) <= 0:
        retpath = SETTINGS.getDefaultAlbumFolderFormat()
    retpath = retpath.replace(R"{ArtistName}", artistName)
    retpath = retpath.replace(R"{AlbumArtistName}", albumArtistName)
    retpath = retpath.replace(R"{Flag}", flag)
    retpath = retpath.replace(R"{AlbumID}", str(album.id))
    retpath = retpath.replace(R"{AlbumYear}", year)
    retpath = retpath.replace(R"{AlbumTitle}", albumName)
    retpath = retpath.replace(R"{AudioQuality}", album.audioQuality)
    retpath = retpath.replace(R"{DurationSeconds}", str(album.duration))
    retpath = retpath.replace(R"{Duration}", __getDurationStr__(album.duration))
    retpath = retpath.replace(R"{NumberOfTracks}", str(album.numberOfTracks))
    retpath = retpath.replace(R"{NumberOfVolumes}", str(album.numberOfVolumes))
    retpath = retpath.replace(R"{ReleaseDate}", str(album.releaseDate))
    retpath = retpath.replace(R"{RecordType}", album.type)
    retpath = retpath.replace(R"{None}", "")
    retpath = retpath.strip()
    return f"{SETTINGS.downloadPath}/{retpath}"

def getPlaylistPath(playlist):
    playlistName = __fixPath__(playlist.title)

    # retpath
    retpath = SETTINGS.playlistFolderFormat
    if retpath is None or len(retpath) <= 0:
        retpath = SETTINGS.getDefaultPlaylistFolderFormat()
    retpath = retpath.replace(R"{PlaylistUUID}", str(playlist.uuid))
    retpath = retpath.replace(R"{PlaylistName}", playlistName)
    return f"{SETTINGS.downloadPath}/{retpath}"


def getTrackPath(track, stream, artist=None, album=None, playlist=None, filename=None):
    print('getTrackPath')
    base = './'
    number = str(track.trackNumber).rjust(2, '0')
    if album is not None:
        base = getAlbumPath(album)
        print(base)
        if album.numberOfVolumes > 1:
            base += f'/CD{str(track.volumeNumber)}'

    if playlist is not None and SETTINGS.usePlaylistFolder:
        base = getPlaylistPath(playlist)
        number = str(track.trackNumberOnPlaylist).rjust(2, '0')
    print('album', album.id)
    # artist
    artists = ""
    if track.artists is not None:
        artists = __fixPath__(getArtistsName(json.dumps(track.artists))) 
    print('artists')

    artist = getTidalArtist(track.artist)
    if artist is not None:
        artist = __fixPath__(artist.name) 
    print('artist')
    # title
    title = __fixPath__(track.title)
    if not aigpy.string.isNull(track.version):
        title += f' ({__fixPath__(track.version)})'

    # explicit
    explicit = "(Explicit)" if track.explicit else ''

    # album and addyear
    albumName = __fixPath__(album.title) if album is not None else ''
    year = __getYear__(album.releaseDate) if album is not None else ''

    # extension
    extension = __getExtension__(stream)

    retpath = SETTINGS.trackFileFormat
    if retpath is None or len(retpath) <= 0:
        retpath = SETTINGS.getDefaultTrackFileFormat()
    retpath = retpath.replace(R"{TrackNumber}", number)
    retpath = retpath.replace(R"{ArtistName}", artist)
    retpath = retpath.replace(R"{ArtistsName}", artists)
    retpath = retpath.replace(R"{TrackTitle}", title)
    retpath = retpath.replace(R"{ExplicitFlag}", explicit)
    retpath = retpath.replace(R"{AlbumYear}", year)
    retpath = retpath.replace(R"{AlbumTitle}", albumName)
    retpath = retpath.replace(R"{AudioQuality}", track.audioQuality)
    retpath = retpath.replace(R"{DurationSeconds}", str(track.duration))
    retpath = retpath.replace(R"{Duration}", __getDurationStr__(track.duration))
    retpath = retpath.replace(R"{TrackID}", str(track.id))
    retpath = retpath.strip()
    if filename is not None:
        return f"{retpath}{extension}"
    else:
        return f"{base}/{retpath}{extension}"

def getTrueHomePath():
    return os.path.join(os.path.dirname(__file__))

def __getHomePath__():
    return os.path.join(os.path.dirname(__file__))+"/config/"

def getLogPath():
    return __getHomePath__() + 'tidalrr.log'

def getTokenPath():
    return __getHomePath__() + 'tidalrr.token.json'

def getProfilePath():
    return __getHomePath__() + 'tidalrr.json'
