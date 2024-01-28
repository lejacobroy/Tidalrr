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

from tidalrr.tidal import *
from tidalrr.workers import *

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

def getMissingAlbums(URL: str, API: str):
    # get missing albums from Lidarr
    albums = []
    try:
        respond = requests.get(URL+'/api/v1/wanted/missing?apikey='+API)
        result = json.loads(respond.text)

        if 'status' not in result:
            #print(result)
            
            for record in result["records"]:
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
        else:
            print(result)
    except Exception as e:
        print("Error getting missing albums: ", e)

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
        album.monitored = 1
        addTidalAlbum(album)
        print('Found album and added to DB: ' + album.title)
