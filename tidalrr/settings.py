#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   settings.py
@Time    :   2020/11/08
@Author  :   Yaronzz
@Version :   3.0
@Contact :   yaronhuang@foxmail.com
@Desc    :
'''
import json
import aigpy
import base64

from tidalrr.model import *
from tidalrr.database import *
from os.path import exists


class Settings(aigpy.model.ModelBase):
    checkExist = True
    includeEP = True
    saveCovers = True
    language = 0
    lyricFile = True
    apiKeyIndex = 4
    showProgress = True
    showTrackInfo = True
    saveAlbumInfo = True
    multiThread = True
    downloadDelay = True
    lidarrURL = ''
    lidarrAPI = ''

    downloadPath = "./download/"
    audioQuality = AudioQuality.Max
    usePlaylistFolder = True
    albumFolderFormat = R"{ArtistName}/{AlbumTitle} [{AlbumYear}] {Flag}"
    playlistFolderFormat = R"Playlist/{PlaylistName} [{PlaylistUUID}]"
    trackFileFormat = R"{TrackNumber} - {ArtistName} - {TrackTitle}{ExplicitFlag}"

    def getDefaultPathFormat(self, type: Type):
        if type == Type.Album:
            return self.albumFolderFormat
        elif type == Type.Playlist:
            return self.playlistFolderFormat
        elif type == Type.Track:
            return self.trackFileFormat
        return ""

    def getAudioQuality(self, value):
        for item in AudioQuality:
            if item.name == value:
                return item
        return self.audioQuality
    
    def read(self):
        settings = getSettings()
        #self._path_ = path
        #txt = aigpy.file.getContent(self._path_)
        #if len(txt) > 0:
        #    data = json.loads(txt)
        if aigpy.model.dictToModel(settings, self) is None:
            # migrate old settings
            path = os.path.join(os.path.dirname(__file__))+'/config/tidalrr.json'
            if exists(path):
                txt = aigpy.file.getContent(path)
                if len(txt) > 0:
                    data = json.loads(txt)
                    if aigpy.model.dictToModel(data, self) is None:
                        return
                    else:
                        self.save()

        self.audioQuality = self.getAudioQuality(self.audioQuality)

        if self.albumFolderFormat is None:
            self.albumFolderFormat = self.getDefaultPathFormat(Type.Album)
        if self.trackFileFormat is None:
            self.trackFileFormat = self.getDefaultPathFormat(Type.Track)
        if self.playlistFolderFormat is None:
            self.playlistFolderFormat = self.getDefaultPathFormat(Type.Playlist)
        if self.apiKeyIndex is None:
            self.apiKeyIndex = 0

    def save(self):
        data = aigpy.model.modelToDict(self)
        data['audioQuality'] = self.audioQuality.name
        #txt = json.dumps(data)
        #aigpy.file.write(self._path_, txt, 'w+')
        setSettings(data)


class TokenSettings(aigpy.model.ModelBase):
    userid = None
    countryCode = None
    accessToken = None
    refreshToken = None
    expiresAfter = 0

    def __encode__(self, string):
        sw = bytes(string, 'utf-8')
        st = base64.b64encode(sw)
        return st

    def __decode__(self, string):
        try:
            sr = base64.b64decode(string)
            st = sr.decode()
            return st
        except:
            return string

    def read(self):
        settings = getSettings()
        #self._path_ = path
        #txt = aigpy.file.getContent(self._path_)
        path = os.path.join(os.path.dirname(__file__))+'/config/tidalrr.token.json'
        if len(settings['tidalToken']) > 0:
            data = json.loads(self.__decode__(settings['tidalToken']))
            aigpy.model.dictToModel(data, self)
        elif exists(path):
            # migrate old token file
            txt = aigpy.file.getContent(path)
            data = json.loads(self.__decode__(txt))
            aigpy.model.dictToModel(data, self)
            self.save()

    def save(self):
        data = aigpy.model.modelToDict(self)
        #txt = json.dumps(data)
        #aigpy.file.write(self._path_, self.__encode__(txt), 'wb')
        #settings = getSettings()
        #settings['tidalToken'] = self.__encode__(json.dumps(data))
        setToken(self.__encode__(json.dumps(data)))


# Singleton
SETTINGS = Settings()
TOKEN = TokenSettings()
