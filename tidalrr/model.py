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
    urls: str

def convertToQueue(queue) -> Queue:
    queueType = Queue(
        id= queue['id'],
        login= queue['login'],
        type= queue['type'],
        path= queue['path'],
        url= queue['url'],
        encryptionKey= queue['encryptionKey'],
        urls= queue['urls']
    )
    return queueType

@dataclass
class File:
    description: str
    type: str
    id : int
    path : str

def convertToFile(file) -> File:
    fileType = File(
        id= file['id'],
        type= file['type'],
        path= file['path'],
        description= file['description']
    )
    return fileType

@dataclass
class Artist:
    id: int
    name : str
    url : str
    path: str
    queued: bool
    downloaded: bool

def convertToArtist(artist) -> Artist:
    artistType = Artist(
        id= artist['id'],
        name= artist['name'],
        url= artist['url'],
        path= artist['path'],
        queued= artist['queued'],
        downloaded= artist['downloaded']
    )
    return artistType

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
    artist : Artist
    artists : Artist
    url : str
    path : str
    queued: bool
    downloaded: bool
    duration : int = 0
    numberOfTracks : int = 0
    numberOfVolumes : int = 0
    version : int = 0

def convertToAlbum(album) -> Album:
    albumType = Album(
        id= album['id'],
        title= album['title'],
        releaseDate= album['releaseDate'],
        type= album['type'],
        cover= album['cover'],
        explicit= album['explicit'],
        audioQuality= album['audioQuality'],
        audioModes= album['audioModes'],
        artist= album['artist'],
        artists= album['artists'],
        url= album['url'],
        duration= album['duration'],
        numberOfTracks=  album['numberOfTracks'],
        numberOfVolumes= album['numberOfVolumes'],
        version= album['version'],
        path= album['path'],
        queued= album['queued'],
        downloaded= album['downloaded']
    )
    return albumType

@dataclass
class Playlist:
    uuid : str
    title : str
    description : str
    image : str
    squareImage : str
    url : str
    path : str
    queued: bool
    downloaded: bool
    numberOfTracks : int = 0
    duration : int = 0

def convertToPlaylist(playlist) -> Playlist:
    playlistType = Playlist(
        uuid= playlist['uuid'],
        title= playlist['title'],
        description= playlist['description'],
        image= playlist['image'],
        squareImage= playlist['squareImage'],
        url= playlist['url'],
        path= playlist['path'],
        queued= playlist['queued'],
        downloaded= playlist['downloaded'],
        numberOfTracks=  playlist['numberOfTracks'],
        duration= playlist['duration']
    )
    return playlistType

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
    path : str
    queued: bool
    downloaded: bool

def convertToTrack(track) -> Track:
    trackType = Track(
        id= track['id'],
        title= track['title'],
        duration= track['duration'],
        trackNumber= track['trackNumber'],
        volumeNumber= track['volumeNumber'],
        trackNumberOnPlaylist= '',
        version= track['version'],
        isrc= track['isrc'],
        explicit= track['explicit'],
        audioQuality= track['audioQuality'],
        audioModes= track['audioModes'],
        copyRight= track['copyright'],
        artist= track['artist'],
        artists= track['artists'],
        album= track['album'],
        allowStreaming='',
        playlist='',
        url= track['url'],
        path= track['path'],
        queued= track['queued'],
        downloaded= track['downloaded']
    )
    return trackType

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


@dataclass
class LoginKey(aigpy.model.ModelBase):
    deviceCode: str
    userCode: str
    verificationUrl: str
    authCheckTimeout: int
    authCheckInterval: int
    userId: str
    countryCode: str
    accessToken: str
    refreshToken: str
    expiresIn: int
    token:str
    clientId:str
    clientSecret:str


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

@dataclass
class Settings:
    albumFolderFormat: str
    apiKeyIndex: int
    audioQuality: str
    checkExist: bool
    downloadDelay: int
    downloadPath: str
    includeEP: bool
    language: str
    lyricFile: str
    multiThread: bool
    playlistFolderFormat: str
    saveAlbumInfo: bool
    saveCovers: bool
    showProgress: bool
    showTrackInfo: bool
    trackFileFormat: str
    usePlaylistFolder: bool
    lidarrUrl: str
    lidarrApi: str
    tidalToken: str
    plexUrl: str
    plexToken: str