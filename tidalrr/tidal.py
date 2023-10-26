#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tidal.py
@Time    :   2019/02/27
@Author  :   Yaronzz
@VERSION :   3.0
@Contact :   yaronhuang@foxmail.com
@Desc    :   tidal api
'''
import json
import random
import re
import time
import aigpy
import datetime
import base64
import requests
from xml.etree import ElementTree
import pandas as pd

from tidalrr.model import *
from tidalrr.settings import *
from tidalrr.paths import *
from tidalrr.apiKey import *

# SSL Warnings | retry number
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 5

""" def getArtistsName(artists=[]):
        array = []
        for item in artists:
            #print(item['name'])
            array.append(item['name'])
        return ", ".join(array) """

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
    
class TidalAPI(object):
    def __init__(self):
        self.key = LoginKey()
        self.apiKey = {'clientId': '7m7Ap0JC9j1cOM3n',
                       'clientSecret': 'vRAdA108tlvkJpTsGZS8rGZ7xTlbJ0qaZ2K9saEzsgY='}

    def __get__(self, path, params={}, urlpre='https://api.tidalhifi.com/v1/'):
        header = {}
        header = {'authorization': f'Bearer {self.key.accessToken}'}
        params['countryCode'] = self.key.countryCode
        errmsg = "Get operation err!"

        #print(urlpre + path, header, params)
        respond = requests.get(urlpre + path, headers=header, params=params)
        #print(respond)
        if respond.url.find("playbackinfopostpaywall") != -1 and SETTINGS.downloadDelay is not False:
            # random sleep between 0.5 and 5 seconds and print it
            sleep_time = random.randint(500, 2000) / 1000
            #print(f"Sleeping for {sleep_time} seconds, to mimic human behaviour and prevent too many requests error")
            time.sleep(sleep_time)

        if respond.status_code == 429:
            print('Too many requests, waiting for 20 seconds...')
            # Loop countdown 20 seconds and print the remaining time
            for i in range(20, 0, -1):
                time.sleep(1)
                #print(i, end=' ')
            #print('')
            

        result = json.loads(respond.text)
        if 'status' not in result:
            #print(result)
            """ if result["totalNumberOfItems"] > 0:
                print('TEST')
                print('TEST',result["items"][0])
                return result.items[0] """
            return result

        if 'userMessage' in result and result['userMessage'] is not None:
            errmsg += result['userMessage']
        

    def __getItems__(self, path, params={}):
        params['limit'] = 50
        params['offset'] = 0
        total = 0
        ret = []
        while True:
            data = self.__get__(path, params)
            if data is None:
                return ret
            if 'totalNumberOfItems' in data:
                total = data['totalNumberOfItems']
            if total > 0 and total <= len(ret):
                return ret

            ret += data["items"]
            num = len(data["items"])
            if num < 50:
                break
            params['offset'] += num
        return ret

    def __post__(self, path, data, auth=None, urlpre='https://auth.tidal.com/v1/oauth2'):
        for index in range(3):
            #try:
            result = requests.post(urlpre+path, data=data, auth=auth, verify=False).json()
            return result
            #except Exception as e:
            #    if index == 2:
            #        raise e

    def getDeviceCode(self) -> str:
        data = {
            'client_id': self.apiKey['clientId'],
            'scope': 'r_usr+w_usr+w_sub'
        }
        result = self.__post__('/device_authorization', data)
        if 'status' in result and result['status'] != 200:
            raise Exception("Device authorization failed. Please choose another apikey.")

        self.key.deviceCode = result['deviceCode']
        self.key.userCode = result['userCode']
        self.key.verificationUrl = result['verificationUri']
        self.key.authCheckTimeout = result['expiresIn']
        self.key.authCheckInterval = result['interval']
        return "http://" + self.key.verificationUrl + "/" + self.key.userCode

    def checkAuthStatus(self) -> bool:
        data = {
            'client_id': self.apiKey['clientId'],
            'device_code': self.key.deviceCode,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
            'scope': 'r_usr+w_usr+w_sub'
        }
        auth = (self.apiKey['clientId'], self.apiKey['clientSecret'])
        result = self.__post__('/token', data, auth)
        if 'status' in result and result['status'] != 200:
            if result['status'] == 400 and result['sub_status'] == 1002:
                return False
            else:
                raise Exception("Error while checking for authorization. Trying again...")

        # if auth is successful:
        self.key.userId = result['user']['userId']
        self.key.countryCode = result['user']['countryCode']
        self.key.accessToken = result['access_token']
        self.key.refreshToken = result['refresh_token']
        self.key.expiresIn = result['expires_in']
        return True

    def verifyAccessToken(self, accessToken) -> bool:
        header = {'authorization': 'Bearer {}'.format(accessToken)}
        result = requests.get('https://api.tidal.com/v1/sessions', headers=header).json()
        if 'status' in result and result['status'] != 200:
            return False
        return True

    def refreshAccessToken(self, refreshToken) -> bool:
        data = {
            'client_id': self.apiKey['clientId'],
            'refresh_token': refreshToken,
            'grant_type': 'refresh_token',
            'scope': 'r_usr+w_usr+w_sub'
        }
        auth = (self.apiKey['clientId'], self.apiKey['clientSecret'])
        result = self.__post__('/token', data, auth)
        if 'status' in result and result['status'] != 200:
            return False

        # if auth is successful:
        self.key.userId = result['user']['userId']
        self.key.countryCode = result['user']['countryCode']
        self.key.accessToken = result['access_token']
        self.key.expiresIn = result['expires_in']
        return True

    def loginByAccessToken(self, accessToken, userid=None):
        header = {'authorization': 'Bearer {}'.format(accessToken)}
        result = requests.get('https://api.tidal.com/v1/sessions', headers=header).json()
        if 'status' in result and result['status'] != 200:
            raise Exception("Login failed!")

        if not aigpy.string.isNull(userid):
            if str(result['userId']) != str(userid):
                raise Exception("User mismatch! Please use your own accesstoken.",)

        self.key.userId = result['userId']
        self.key.countryCode = result['countryCode']
        self.key.accessToken = accessToken
        return

    def convertToAlbum(self, album) -> Album:
        albumType = Album(
           id= album['id'],
           title= album['title'],
           releaseDate= album['releaseDate'],
           type= album['type'],
           cover= album['cover'],
           explicit= album['explicit'],
           audioQuality= album['audioQuality'],
           audioModes= json.dumps(album['audioModes']),
           path= '',
           artist= album['artist']['id'],
           artists= json.dumps(album['artists']),
           url= album['url'],
           duration= album['duration'],
           numberOfTracks=  album['numberOfTracks'],
           numberOfVolumes= album['numberOfVolumes'],
           version= album['version']
        )
        albumType.path = getAlbumPath(albumType)

        return albumType

    def getAlbum(self, id) -> Album:
        album = self.__get__('albums/' + str(id))
        return self.convertToAlbum(album)
    
    def searchAlbum(self, obj) -> Album:
        #print(aigpy.model.modelToDict(obj))
        name = str(obj.artist.name +' - '+ obj.title)

        # Transform json input to python objects
        input_dict = self.__get__('albums?query='+str(name), {}, 'https://api.tidalhifi.com/v1/search/')["items"]

        # Filter python objects with list comprehensions
        # x["numberOfTracks"] == obj.numberOfTracks and
        output_dict = [x for x in input_dict if  x["title"] == obj.title and x["artist"]["name"] == obj.artist.name]
        # filter by artist and album title
        if len(output_dict) == 0:
            print('no album matched')
            return
        return self.convertToAlbum(output_dict[0])
    
    def getPlaylistsAndFavorites(self, userId=None) -> Playlist:
        # Transform json input to python objects
        input_dict = self.__get__(str(self.key.userId)+'/playlistsAndFavoritePlaylists', {}, 'https://api.tidalhifi.com/v1/users/')["items"]
        playlists = [Playlist()]
        if len(input_dict) == 0:
            print('no playlists')
            return
        for item in input_dict:
            playlists.append(Playlist(*item["playlist"]))
        return playlists


    def getPlaylist(self, id) -> Playlist:
        return Playlist(*self.__get__('playlists/' + str(id)))

    def convertToArtist(self, artist) -> Artist:
        artistType = Artist(
            id= artist['id'],
            name= artist['name'],
            url= artist['url']
        )
        return artistType
    
    def getArtist(self, id) -> Artist:
        artist = self.__get__('artists/' + str(id))
        return self.convertToArtist(artist)

    def convertToTrack(self, track) -> Track:
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
            audioModes= json.dumps(track['audioModes']),
            copyRight= track['copyright'],
            artist= track['artist']['id'],
            artists= json.dumps(track['artists']),
            album= track['album']['id'],
            allowStreaming='',
            playlist='',
            url= track['url'],
        )
        return trackType

    def getTrack(self, id) -> Track:
        track = self.__get__('tracks/' + str(id))
        return self.convertToTrack(track)

    def getMix(self, id) -> Mix:
        mix = Mix()
        mix.id = id
        mix.tracks = self.getItems(id, Type.Mix)
        return None, mix

    def getTypeData(self, id, type: Type):
        if type == Type.Album:
            print('getTypeData', id)
            return self.getAlbum(id)
        if type == Type.Artist:
            return self.getArtist(id)
        if type == Type.Track:
            return self.getTrack(id)
        if type == Type.Playlist:
            return self.getPlaylist(id)
        if type == Type.Mix:
            return self.getMix(id)
        return None

    def search(self, text: str, type: Type, offset: int = 0, limit: int = 10) -> SearchResult:
        typeStr = type.name.upper() + "S"
        if type == Type.Null:
            typeStr = "ARTISTS,ALBUMS,TRACKS,PLAYLISTS"

        params = {"query": text,
                  "offset": offset,
                  "limit": limit,
                  "types": typeStr}
        return aigpy.model.dictToModel(self.__get__('search', params=params), SearchResult())

    def getSearchResultItems(self, result: SearchResult, type: Type):
        if type == Type.Track:
            return result.tracks.items
        if type == Type.Album:
            return result.albums.items
        if type == Type.Artist:
            return result.artists.items
        if type == Type.Playlist:
            return result.playlists.items
        return []

    def getLyrics(self, id) -> Lyrics:
        data = self.__get__(f'tracks/{str(id)}/lyrics', urlpre='https://listen.tidal.com/v1/')
        return aigpy.model.dictToModel(data, Lyrics())

    def getItems(self, id, type: Type):
        if type == Type.Playlist:
            data = self.__getItems__('playlists/' + str(id) + "/items")
        elif type == Type.Album:
            data = self.__getItems__('albums/' + str(id) + "/items")
        elif type == Type.Mix:
            data = self.__getItems__('mixes/' + str(id) + '/items')
        else:
            raise Exception("invalid Type!")
        tracks = []
        for item in data:
            if item['type'] == 'track' and item['item']['streamReady']:
                tracks.append(self.convertToTrack(item['item']))
        return tracks

    def orderHighQAlbums(self, data=[]) -> [Album]:
        filteredAlbums = []
        for album in data:
            if 'title' in album.keys() and 'audioQuality' in album.keys():
                filteredAlbums.append(album)

        for i, item in enumerate(filteredAlbums):
            filteredAlbums[i]['nquality'] = 0
            if item['audioQuality'] == "HIGH":
                filteredAlbums[i]['nquality'] = 1
            elif item['audioQuality'] == "HI_RES":
                filteredAlbums[i]['nquality'] = 2
            elif item['audioQuality'] == "LOSSLESS":
                filteredAlbums[i]['nquality'] = 3
            elif item['audioQuality'] == "HI_RES_LOSSLESS":
                filteredAlbums[i]['nquality'] = 4

        # get a list of duplicated album.name
        df = pd.DataFrame(filteredAlbums)
        df.sort_values(by=['title', 'nquality'], inplace=True)
        df.drop_duplicates(subset=['title'], keep='last', inplace=True)
        new_albums = df.to_dict("records")

        albums = list(self.convertToAlbum(item) for item in new_albums)
        return albums

    def getArtistAlbums(self, id, includeEP=False):
        data = self.__getItems__(f'artists/{str(id)}/albums')
        albums = []
        if len(data) > 0 :
            albums = self.orderHighQAlbums(data)

            if not includeEP:
                return albums

            data = self.__getItems__(f'artists/{str(id)}/albums', {"filter": "EPSANDSINGLES"})
            if len(data) > 0 :
                albums += self.orderHighQAlbums(data)

        return albums
    
    # from https://github.com/Dniel97/orpheusdl-tidal/blob/master/interface.py#L582
    def parse_mpd(self, xml: bytes) -> list:
        # Removes default namespace definition, don't do that!
        xml = re.sub(r'xmlns="[^"]+"', '', xml, count=1)
        root = ElementTree.fromstring(xml)

        # List of AudioTracks
        tracks = []

        for period in root.findall('Period'):
            for adaptation_set in period.findall('AdaptationSet'):
                for rep in adaptation_set.findall('Representation'):
                    # Check if representation is audio
                    content_type = adaptation_set.get('contentType')
                    if content_type != 'audio':
                        raise ValueError('Only supports audio MPDs!')

                    # Codec checks
                    codec = rep.get('codecs').upper()
                    if codec.startswith('MP4A'):
                        codec = 'AAC'

                    # Segment template
                    seg_template = rep.find('SegmentTemplate')
                    # Add init file to track_urls
                    track_urls = [seg_template.get('initialization')]
                    start_number = int(seg_template.get('startNumber') or 1)

                    # https://dashif-documents.azurewebsites.net/Guidelines-TimingModel/master/Guidelines-TimingModel.html#addressing-explicit
                    # Also see example 9
                    seg_timeline = seg_template.find('SegmentTimeline')
                    if seg_timeline is not None:
                        seg_time_list = []
                        cur_time = 0

                        for s in seg_timeline.findall('S'):
                            # Media segments start time
                            if s.get('t'):
                                cur_time = int(s.get('t'))

                            # Segment reference
                            for i in range((int(s.get('r') or 0) + 1)):
                                seg_time_list.append(cur_time)
                                # Add duration to current time
                                cur_time += int(s.get('d'))

                        # Create list with $Number$ indices
                        seg_num_list = list(range(start_number, len(seg_time_list) + start_number))
                        # Replace $Number$ with all the seg_num_list indices
                        track_urls += [seg_template.get('media').replace('$Number$', str(n)) for n in seg_num_list]

                    tracks.append(track_urls)
        return tracks

    def getStreamUrl(self, id, quality: AudioQuality):
        squality = "HI_RES"
        if quality == AudioQuality.Normal:
            squality = "LOW"
        elif quality == AudioQuality.High:
            squality = "HIGH"
        elif quality == AudioQuality.HiFi:
            squality = "LOSSLESS"
        elif quality == AudioQuality.Max:
            squality = "HI_RES_LOSSLESS"

        paras = {"audioquality": squality, "playbackmode": "STREAM", "assetpresentation": "FULL"}
        data = self.__get__(f'tracks/{str(id)}/playbackinfopostpaywall', paras)
        resp = aigpy.model.dictToModel(data, StreamRespond())
        if hasattr(resp, 'manifestMimeType'):
            if "vnd.tidal.bt" in resp.manifestMimeType:
                manifest = json.loads(base64.b64decode(resp.manifest).decode('utf-8'))
                ret = StreamUrl()
                ret.trackid = resp.trackid
                ret.soundQuality = resp.audioQuality
                ret.codec = manifest['codecs']
                ret.encryptionKey = manifest['keyId'] if 'keyId' in manifest else ""
                ret.url = manifest['urls'][0]
                ret.urls = [ret.url]
                return ret
            elif "dash+xml" in resp.manifestMimeType:
                xmldata = base64.b64decode(resp.manifest).decode('utf-8')
                ret = StreamUrl()
                ret.trackid = resp.trackid
                ret.soundQuality = resp.audioQuality
                ret.codec = aigpy.string.getSub(xmldata, 'codecs="', '"')
                ret.encryptionKey = ""#manifest['keyId'] if 'keyId' in manifest else ""
                ret.urls = self.parse_mpd(xmldata)[0]
                if len(ret.urls) > 0:
                    ret.url = ret.urls[0]
                return ret
        else:
            print("Can't get the streamUrl, resp is None")
        # else:
        #     manifest = json.loads(base64.b64decode(resp.manifest).decode('utf-8'))
        #raise Exception("Can't get the streamUrl, type is " + resp.manifestMimeType)

    def getTrackContributors(self, id):
        return self.__get__(f'tracks/{str(id)}/contributors')

    def getCoverUrl(self, sid):
        if sid is None:
            return ""
        return f"https://resources.tidal.com/images/{sid.replace('-', '/')}/origin.jpg"

    def getCoverData(self, sid):
        url = self.getCoverUrl(sid)
        #try:
        return requests.get(url).content
        #except:
        #    return ''

    def parseUrl(self, url):
        if "tidal.com" not in url:
            return Type.Null, url

        url = url.lower()
        for index, item in enumerate(Type):
            if item.name.lower() in url:
                etype = item
                return etype, aigpy.string.getSub(url, etype.name.lower() + '/', '/')
        return Type.Null, url

    def getByString(self, string):
        if aigpy.string.isNull(string):
            raise Exception("Please enter something.")

        obj = None
        etype, sid = self.parseUrl(string)
        for index, item in enumerate(Type):
            if etype != Type.Null and etype != item:
                continue
            if item == Type.Null:
                continue
            
            obj = self.getTypeData(sid, item)
            return item, obj
        

        raise Exception("No result.")


# Singleton
TIDAL_API = TidalAPI()
