#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   lidarr.py
@Time    :   2023/04/12
@Author  :   lejacobroy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
import requests
import json
from tidalrr.model import Album
from tidalrr.tidal import TIDAL_API
from tidalrr.database import getSettings
from tidalrr.database.albums import addTidalAlbum
from tidalrr.database.artists import addTidalArtist, getTidalArtist

def syncLidarr():
    settings = getSettings()
    albums = [Album]
    albums = getMissingAlbums(settings.lidarrUrl, settings.lidarrApi)
    print('Scanning '+str(len(albums))+' missing albums')
    for album in albums :
        if album['title'] is not None:    
            # set download path
            # settings.downloadPath = str(album.path)
            start_album_search(album)

def getLidarrMissingRecords(URL: str, API: str, page: int = 1):
    try:
        respond = requests.get(URL+'/api/v1/wanted/missing?apikey='+API+'&pageSize=10&page='+str(page))
        return json.loads(respond.text)
    except Exception as e:
        print("Error getting missing albums: ", e)
        return ''

def getMissingAlbums(URL: str, API: str):
    # get missing albums from Lidarr
    albums = []
    page = 1
    result = getLidarrMissingRecords(URL, API, page)
    if 'status' not in result:
        allMissingRecords = []
        while result['records']!= []:
            allMissingRecords.extend(result['records'])
            page += 1
            result = getLidarrMissingRecords(URL, API, page)
    else:
        print(result)
        return albums

    for record in allMissingRecords:
        artistId = 0

        for link in record['artist']['links']:
            if link['name'] == 'tidal':
                artistId = int(link['url'].split('/')[-1])
        album = {
            'title': record['title'],
            'artist': record['artist']['artistName'],
            'artistId': artistId,
        }
        #print(album)
        albums.append(album)


    return albums

    # returns this:
    # extract usefull info:
    #   - Artist, Title, Path
    # match "Artist - Album Title" with a Tidal ID (API Search?)
    # https://github.com/Fokka-Engineering/TIDAL/wiki/search-artists -> get artist ID
    #    -> https://api.tidalhifi.com/v1/search/artists?query='Coldplay'&limit=1&countryCode=CA
    # https://github.com/Fokka-Engineering/TIDAL/wiki/search-albums -> get album ID and filter by artist ID

def start_album_search(alb: Album):
    #print(aigpy.model.modelToDict(obj))
    album = TIDAL_API.searchAlbum(alb)
    if album is not None:
        artist = getTidalArtist(album.artist)
        if artist is None:
            artist = TIDAL_API.getArtist(album.artist)
            artist.monitored = False
            addTidalArtist(artist)
            print('Found artist and added to DB: ' + artist.name)

        album.monitored = True
            
        addTidalAlbum(album)
        print('Found album and added to DB: ' + album.title)
