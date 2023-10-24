#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   model.py
@Time    :   2020/08/08
@Author  :   Yaronzz
@Version :   3.0
@Contact :   yaronhuang@foxmail.com
@Desc    :   
'''
import aigpy
from dataclasses import dataclass
from enum import Enum


class AudioQuality(Enum):
    Normal = 0
    High = 1
    HiFi = 2
    Master = 3
    Max = 4

class Type(Enum):
    Album = 0
    Track = 1
    Playlist = 3
    Artist = 4
    Mix = 5
    Null = 6
    
class StreamUrl(aigpy.model.ModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.trackid = None
        self.url = None
        self.urls = None
        self.codec = None
        self.encryptionKey = None
        self.soundQuality = None

@dataclass
class Queue:
    url : str
    type : str
    login : bool
    id : int
    path : str
    encryptionKey: str

@dataclass
class File:
    description: str
    type: str
    id : int
    path : str

@dataclass
class Artist:
    id: int
    name : str
    url : str

@dataclass
class Album:
    id : int
    title : str
    releaseDate : str
    type : str
    cover : str
    explicit : bool
    audioQuality : str
    audioModes : str
    path : str
    artist : Artist
    artists : Artist
    url : str
    duration : int = 0
    numberOfTracks : int = 0
    numberOfVolumes : int = 0
    version : int = 0

@dataclass
class Playlist:
    uuid : str
    title : str
    description : str
    image : str
    squareImage : str
    url : str
    numberOfTracks : int = 0
    duration : int = 0

@dataclass
class Track:
    id : int
    title : str
    duration : int
    trackNumber : int
    volumeNumber : int
    trackNumberOnPlaylist : int
    version : str
    isrc : str
    explicit : bool
    audioQuality : str
    audioModes: None
    copyRight: str
    artist : Artist
    artists : Artist
    album : Album
    allowStreaming : None
    playlist : None
    url : str

class Mix(aigpy.model.ModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.id = None
        self.tracks = Track()


class Lyrics(aigpy.model.ModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.trackId = None
        self.lyricsProvider = None
        self.providerCommontrackId = None
        self.providerLyricsId = None
        self.lyrics = None
        self.subtitles = None


class SearchDataBase(aigpy.model.ModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.limit = 0
        self.offset = 0
        self.totalNumberOfItems = 0


class SearchAlbums(SearchDataBase):
    def __init__(self) -> None:
        super().__init__()
        self.items = Album()


class SearchArtists(SearchDataBase):
    def __init__(self) -> None:
        super().__init__()
        self.items = Artist()


class SearchTracks(SearchDataBase):
    def __init__(self) -> None:
        super().__init__()
        self.items = Track()


class SearchPlaylists(SearchDataBase):
    def __init__(self) -> None:
        super().__init__()
        self.items = Playlist()


class SearchResult(aigpy.model.ModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.artists = SearchArtists()
        self.albums = SearchAlbums()
        self.tracks = SearchTracks()
        self.playlists = SearchPlaylists()


class LoginKey(aigpy.model.ModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.deviceCode = None
        self.userCode = None
        self.verificationUrl = None
        self.authCheckTimeout = None
        self.authCheckInterval = None
        self.userId = None
        self.countryCode = None
        self.accessToken = None
        self.refreshToken = None
        self.expiresIn = None


class StreamRespond(aigpy.model.ModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.trackid = None
        self.streamType = None
        self.assetPresentation = None
        self.audioMode = None
        self.audioQuality = None
        self.manifestMimeType = None
        self.manifest = None

class Settings (aigpy.model.ModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.albumFolderFormat = None
        self.apiKeyIndex = None
        self.audioQuality = None
        self.checkExist = None
        self.downloadDelay = None
        self.downloadPath = None
        self.includeEP = None
        self.language = None
        self.lyricFile = None
        self.multiThread = None
        self.playlistFolderFormat = None
        self.saveAlbumInfo = None
        self.saveCovers = None
        self.showProgress = None
        self.showTrackInfo = None
        self.trackFileFormat = None
        self.usePlaylistFolder = None
        self.lidarrUrl = None
        self.lidarrApi = None
        self.tidalToken = None
        self.plexUrl = None
        self.plexToken = None