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
import subprocess
import sys
import aigpy
import base64
import requests
from xml.etree import ElementTree
import pandas as pd

from tidalrr.model import *
from tidalrr.paths import *
from tidalrr.apiKey import *

# SSL Warnings | retry number
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 5

def tidalLogin():
    url = ''
    timeout = ''
    settings = getSettings()
    key = getTidalKey()
    if len(key.accessToken) > 0:
        print('Non-Empty Access Token, logging in')
        try:
            loginByAccessToken(key.accessToken, key.userId)
        except:
            print('Login failed')
            key.accessToken = ''
            setTidalKey(key)
    if not isItemValid(settings.apiKeyIndex):
        print('API Key invalid')
        changeApiKey()
        url, timeout = startWaitForAuth()
        
    elif not loginByConfig():
        print('Login By Config failed')
        url, timeout = startWaitForAuth()
    if url != '':
        print('Login URL was set, Waiting for Auth...')
        print (url, timeout)
    return url, timeout

def startWaitForAuth():
    url = getDeviceCode()
    key = getTidalKey()
    timeout = displayTime(int(key.authCheckTimeout))
    # start subprocess to waitFroAuth()
    try:
        process = subprocess.Popen([sys.executable, 'runWaitForAuth.py'])
    except subprocess.CalledProcessError as e:
        return f"Script execution failed: {e.output}"
    print(url, timeout)
    return url, timeout

def changeApiKey():
    settings = getSettings()
    item = getItem(settings.apiKeyIndex)
    ver = getVersion()

    print(f'Current APIKeys: {str(settings.apiKeyIndex)} {item["platform"]}-{item["formats"]}')
    print(f'Current Version: {str(ver)}')
    print(getItems())
    index = int(print("APIKEY index:",getLimitIndexs()))

    if index != settings.apiKeyIndex:
        settings.apiKeyIndex = index
        setSettings(settings)
        return True
    return False


def displayTime(seconds, granularity=2):
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
        url = getDeviceCode()
        key = getTidalKey()
        print(displayTime(int(key.authCheckTimeout)), " " + url)
 
        return waitForAuth()
    except Exception as e:
        print(f"Login failed.{str(e)}")
        return False


def waitForAuth():
    try:
        start = time.time()
        elapsed = 0
        key = getTidalKey()
        if key.deviceCode == '':
            getDeviceCode()
        while elapsed < int(key.authCheckTimeout):
            elapsed = time.time() - start
            if not checkAuthStatus():
                time.sleep(int(key.authCheckInterval) + 1)
                print('Waiting for Auth')
                continue
            #key.expiresAfter = time.time() + int(key.expiresIn)
            #setTidalKey(key)
            print('Auth is good')
            return True

        raise Exception()
    except Exception as e:
        print(f"Login failed.{str(e)}")
        return False

def loginByConfig():
    key = getTidalKey()
    if key.deviceCode == '':
            getDeviceCode()
    try:
        if key.accessToken is None:
            return False

        if verifyAccessToken(key.accessToken):
            return True

        if refreshAccessToken(key.refreshToken):
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

def getDeviceCode() -> str:
    key = getTidalKey()
    data = {
        'client_id': key.clientId,
        'scope': 'r_usr+w_usr+w_sub'
    }
    result = post('/device_authorization', data)
    if 'status' in result and result['status'] != 200:
        raise Exception("Device authorization failed. Please choose another apikey.")
    #print('deviceCode', result)
    key.deviceCode = result['deviceCode']
    key.userCode = result['userCode']
    key.verificationUrl = result['verificationUri']
    key.authCheckTimeout = result['expiresIn']
    key.authCheckInterval = result['interval']
    setTidalKey(key)
    return "http://" + key.verificationUrl + "/" + key.userCode

def post(path, data, auth=None, urlpre='https://auth.tidal.com/v1/oauth2'):
    for index in range(3):
        try:
            result = requests.post(urlpre+path, data=data, auth=auth, verify=False).json()
            return result
        except Exception as e:
            if index == 2:
                raise e

def checkAuthStatus() -> bool:
    key = getTidalKey()
    data = {
        'client_id': key.clientId,
        'device_code': key.deviceCode,
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'scope': 'r_usr+w_usr+w_sub'
    }
    auth = (key.clientId, key.clientSecret)
    result = post('/token', data, auth)
    #print(data, result)
    if 'status' in result and result['status'] != 200:
        if result['status'] == 400 and result['sub_status'] == 1002:
            return False
        else:
            raise Exception("Error while checking for authorization. Trying again...")
    # if auth is successful:
    key.userId = result['user']['userId']
    key.countryCode = result['user']['countryCode']
    key.accessToken = result['access_token']
    key.refreshToken = result['refresh_token']
    key.expiresIn = result['expires_in']
    setTidalKey(key)
    return True

def verifyAccessToken(accessToken) -> bool:
    header = {'authorization': 'Bearer {}'.format(accessToken)}
    result = requests.get('https://api.tidal.com/v1/sessions', headers=header).json()
    #print('verify',result)
    if 'status' in result and result['status'] != 200:
        return False
    """    # Set tidalapi session.
    self.session = tidalapi.session.Session()
    self.session.load_oauth_session("Bearer", accessToken) """
    return True

def refreshAccessToken(refreshToken) -> bool:
    key = getTidalKey()
    data = {
        'client_id': key.clientId,
        'refresh_token': refreshToken,
        'grant_type': 'refresh_token',
        'scope': 'r_usr+w_usr+w_sub'
    }
    auth = (key.clientId, key.clientSecret)
    result = post('/token', data, auth)
    if 'status' in result and result['status'] != 200:
        return False
    # if auth is successful:
    #print('refresh',result)
    key.userId = result['user']['userId']
    key.countryCode = result['user']['countryCode']
    key.accessToken = result['access_token']
    key.expiresIn = result['expires_in']
    setTidalKey(key)
    return True

def loginByAccessToken(accessToken, userid=None):
    key = getTidalKey()
    header = {'authorization': 'Bearer {}'.format(accessToken)}
    result = requests.get('https://api.tidal.com/v1/sessions', headers=header).json()
    if 'status' in result and result['status'] != 200:
        raise Exception("Login failed!")

    if not aigpy.string.isNull(userid):
        if str(result['userId']) != str(userid):
            raise Exception("User mismatch! Please use your own accesstoken.",)
    #print('login',result)
    key.userId = result['userId']
    key.countryCode = result['countryCode']
    key.accessToken = accessToken
    setTidalKey(key)
    return

def setLowerQuality():
    settings = getSettings()
    if settings.audioQuality == 'Max':
        settings.audioQuality = 'Master'
    elif settings.audioQuality == 'Master':
        settings.audioQuality = 'HiFi'
    elif settings.audioQuality == 'HiFi':
        settings.audioQuality = 'High'
    elif settings.audioQuality == 'High':
        settings.audioQuality = 'Normal'
    elif settings.audioQuality == 'Normal':
        print('User cannot stream, you must have an active subscription')
    setSettings(settings)


class TidalAPI(object):
    def __init__(self):
        createTables()
        self.key = getTidalKey()
        self.key.clientId = '7m7Ap0JC9j1cOM3n'
        self.key.clientSecret ='vRAdA108tlvkJpTsGZS8rGZ7xTlbJ0qaZ2K9saEzsgY='
        setTidalKey(self.key)

    def __get__(self, path, params={}, urlpre='https://api.tidalhifi.com/v1/'):
        header = {}
        header = {'authorization': f'Bearer {self.key.accessToken}'}
        params['countryCode'] = self.key.countryCode
        errmsg = "Get operation err!"
        for index in range(0, 3):
            try:
                respond = requests.get(urlpre + path, headers=header, params=params)
                #print(respond.text)
                if respond.text == 'The token has expired. (Expired on time)':
                    # need to reauth user
                    if loginByConfig():
                        print('loginByConfig returned true')
                        self.__get__(self, path, params, urlpre)
                        continue
                    else: 
                        print('loginByConfig returned false, breaking loop')
                        break
                if respond.url.find("playbackinfopostpaywall") != -1 :
                    # random sleep between 0.5 and 5 seconds and print it
                    sleep_time = random.randint(500, 2000) / 1000
                    #print(f"Sleeping for {sleep_time} seconds, to mimic human behaviour and prevent too many requests error")
                    time.sleep(sleep_time)

                if respond.status_code == 429 or respond.text == 'Asset is not ready for playback':
                    print('Too many requests, waiting for 20 seconds...')
                    # Loop countdown 20 seconds and print the remaining time
                    for i in range(20, 0, -1):
                        time.sleep(1)
                        #print(i, end=' ')
                    #print('')
                    continue
                    
                result = json.loads(respond.text)
                if 'status' not in result:
                    return result

                if 'userMessage' in result and result['userMessage'] is not None:
                    errmsg += result['userMessage']
                    if result['userMessage'] == "Requested quality is not allowed in user's subscription":
                        #set lower quality
                        print('setting lower quality')
                        setLowerQuality()
                break
            except Exception as e:
                if index >= 3:
                    errmsg += respond.text

        raise Exception(errmsg)


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

    def getAlbum(self, id) -> Album:
        album = self.__get__('albums/' + str(id))
        album['audioModes'] = json.dumps(album['audioModes'])
        album['artists'] = json.dumps(album['artists'])
        album['path'] = ''
        album['queued'] = False
        album['downloaded'] = False
        album['artist'] = album['artist']['id']
        convertedAlbum = convertToAlbum(album)
        convertedAlbum.path = getAlbumPath(convertedAlbum)
        return convertedAlbum
    
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
        output_dict[0]['audioModes'] = json.dumps(output_dict[0]['audioModes'])
        output_dict[0]['artists'] = json.dumps(output_dict[0]['artists'])
        output_dict[0]['path'] = ''
        output_dict[0]['queued'] = False
        output_dict[0]['downloaded'] = False
        output_dict[0]['artist'] = output_dict[0]['artist']['id']
        convertedAlbum = convertToAlbum(output_dict[0])
        convertedAlbum.path = getAlbumPath(convertedAlbum)

        return convertToAlbum(output_dict[0])
    
    def getPlaylistsAndFavorites(self, userId=None) -> Playlist:
        settings = getSettings()
        # Transform json input to python objects
        input_dict = self.__get__(str(self.key.userId)+'/playlistsAndFavoritePlaylists', {}, 'https://api.tidalhifi.com/v1/users/')["items"]
        playlists = [Playlist]
        if len(input_dict) == 0:
            print('no playlists')
            return
        for item in input_dict:
            item["playlist"]['path'] = f"{settings.downloadPath}/Playlists/{fixPath(item['playlist']['title'])}"
            item["playlist"]['queued'] = False
            item["playlist"]['downloaded'] = False
            item["playlist"]['plexUUID'] = ''
            playlists.append(convertToPlaylist(item["playlist"]))
        return playlists


    def getPlaylist(self, id) -> Playlist:
        settings = getSettings()
        playlist = self.__get__('playlists/' + str(id))
        playlist['path'] = f"{settings.downloadPath}/Playlists/{fixPath(playlist['title'])}"
        playlist['queued'] = False
        playlist['downloaded'] = False
        playlist['plexUUID'] = ''
        return convertToPlaylist(playlist)
    
    def getArtist(self, id) -> Artist:
        settings = getSettings()
        artist = self.__get__('artists/' + str(id))
        artist['path'] = f"{settings.downloadPath}/{fixPath(artist['name'])}"
        artist['queued'] = False
        artist['downloaded'] = False
        return convertToArtist(artist)

    def getTrack(self, id) -> Track:
        track = self.__get__('tracks/' + str(id))
        track['path'] = ''
        track['queued'] = False
        track['downloaded'] = False
        track['plexUUID'] = ''
        return convertToTrack(track)

    def getMix(self, id) -> Mix:
        mix = Mix()
        mix.id = id
        mix.tracks = self.getItems(id, Type.Mix)
        return None, mix

    def getTypeData(self, id, type: Type):
        if type == Type.Album:
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
                item['item']['path'] = ''
                item['item']['queued'] = False
                item['item']['downloaded'] = False
                item['item']['artist'] = item['item']['artist']['id']
                item['item']['album'] = item['item']['album']['id']
                item['item']['audioModes'] = json.dumps(item['item']['audioModes'])
                item['item']['artists'] = json.dumps(item['item']['artists'])
                item['item']['plexUUID'] = ''
                tracks.append(convertToTrack(item['item']))
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

        albums = [Album]
        for i,album in enumerate(new_albums):
            new_albums[i]['audioModes'] = json.dumps(new_albums[i]['audioModes'])
            new_albums[i]['artists'] = json.dumps(new_albums[i]['artists'])
            new_albums[i]['path'] = ''
            new_albums[i]['queued'] = False
            new_albums[i]['downloaded'] = False
            new_albums[i]['artist'] = new_albums[i]['artist']['id']
            convertedAlbum = convertToAlbum(new_albums[i])
            convertedAlbum.path = getAlbumPath(convertedAlbum)
            albums.append(convertedAlbum)
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
        squality = ""
        if quality == 'Normal':
            squality = "LOW"
        elif quality == 'High':
            squality = "HIGH"
        elif quality == 'HiFi':
            squality = "HI_RES"
        elif quality == 'Master':
            squality = "LOSSLESS"
        elif quality == 'Max':
            squality = "HI_RES_LOSSLESS"
        paras = {"audioquality": squality, "playbackmode": "STREAM", "assetpresentation": "FULL"}
        data = self.__get__(f'tracks/{str(id)}/playbackinfopostpaywall', paras)
        resp = aigpy.model.dictToModel(data, StreamRespond())

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
            ret.codec = "DASH-"+aigpy.string.getSub(xmldata, 'codecs="', '"')
            ret.encryptionKey = ""  # manifest['keyId'] if 'keyId' in manifest else ""
            ret.urls = self.parse_mpd(xmldata)[0]
            if len(ret.urls) > 0:
                ret.url = ret.urls[0]
            return ret

        raise Exception("Can't get the streamUrl, type is " + resp.manifestMimeType)


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
