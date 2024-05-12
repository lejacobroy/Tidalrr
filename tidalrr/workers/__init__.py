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
import time
import aigpy
import requests
import functools
import os
from pathlib import Path
from tidalrr.tidal import TIDAL_API, tidalLogin
from tidalrr.model import Queue,  Track, Settings, Album, Artist, Playlist
from tidalrr.paths import getAlbumPath
from tidalrr.database import getSettings, createTables
from tidalrr.database.files import getFileById
from tidalrr.database.queues import addTidalQueue
from tidalrr.database.playlists import getDownloadedTidalPlaylists, getTidalPlaylistTracks
from tidalrr.database.artists import getTidalArtist
import logging

logger = logging.getLogger(__name__)

# This decorator can be applied to any job function to log the elapsed time of each job
def print_elapsed_time(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_timestamp = time.time()
        print('LOG: Running job "%s"' % func.__name__)
        result = func(*args, **kwargs)
        print('LOG: Job "%s" completed in %d seconds' % (func.__name__, time.time() - start_timestamp))
        return result

    return wrapper

def tidalrrStart():
    createTables()
    tidalLogin()

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

    obj.albumartist = artist
    obj.date = album.releaseDate
    obj.totaldisc = album.numberOfVolumes
    obj.lyrics = lyrics
    if obj.totaldisc <= 1:
        obj.totaltrack = album.numberOfTracks
    coverpath = TIDAL_API.getCoverUrl(album.cover)
    obj.save(coverpath)

def fileExists(finalpath, url):
    settings = getSettings()
    if not settings.checkExist:
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

def scanCover(album):
    cover = getFileById(album.id)
    if cover is None:
        if album is None:
            return
        path = getAlbumPath(album) 
        if path is not None:
            path = path + '/cover.jpg'
            url = TIDAL_API.getCoverUrl(album.cover)

            queue = Queue(
                type='Cover',
                login=False,
                id=album.id,
                path=path,
                url=url,
                encryptionKey='',
                urls = [url]
            )

            addTidalQueue(queue)
            #aigpy.net.downloadFile(url, path)

def download_file_part(path, url, part_number):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        file_name = f'{path}_{part_number}.part'

        with open(file_name, 'wb') as file:
            file.write(response.content)

        logging.info(f'Downloaded part {part_number} from')
        return file_name, None

    except requests.RequestException as e:
        logging.error(f'Error downloading part {part_number} from : {e}')
        return False, str(e)

def combine_file_parts(output_file, *file_parts):
    # verify that all the file parts have downloaded successfully
    for file in file_parts:
        if not os.path.isfile(file):
            print('File part not found', file)
            return False
    try:
        with open(output_file, 'wb') as output:
            for part in file_parts:
                with open(part, 'rb') as file_part:
                    output.write(file_part.read())

        logging.info(f'Combined file saved as {output_file}')

    except Exception as e:
        logging.error(f'Error combining file parts: {e}')
        return False, str(e)

def download_and_combine(path, urls):
    file_parts = []
    err = None
    # Extract the directory path from the file path
    directory_path = os.path.dirname(path)

    # Create the directory structure if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)

    for i, url in enumerate(urls):
        part_number = i + 1
        file_part, err = download_file_part(path, url, part_number)

        if file_part:
            file_parts.append(file_part)
        else:
            # Skip to the next URL if there's an error downloading a part
            continue

    result = combine_file_parts(path, *file_parts)
    # Clean up: delete individual file parts
    for file_part in file_parts:
        try:
            os.remove(file_part)
            logging.info(f'Deleted file part: {file_part}')
            result = True
        except Exception as e:
            logging.error(f'Error deleting file part {file_part}: {e}')
            return False, str(e)
    return result, err

def updatePlaylistsFiles():
    settings = getSettings()
    
    # get all downloaded playlists 
    playlists = getDownloadedTidalPlaylists()
    for i, playlist in enumerate(playlists):
        tracks = getTidalPlaylistTracks(playlist.uuid)
        for index, track in enumerate(tracks):
            if hasattr(track, 'id'):
                tracks[index].trackNumberOnPlaylist = index + 1

        # Generate m3u playlist file
        generateM3uFile(settings, playlist, tracks)

        # Generate m3u8 playlist file
        generateM3u8File(settings, playlist, tracks)
        print('Generated files for playlist '+str(i)+'/'+str(len(playlists))+': '+playlist.title)

def generateM3uFile(settings: Settings, playlist: Playlist, tracks: list[Track]):
    plexPath = ''
    if settings.plexHomePath != '':
        plexPath = settings.plexHomePath
    try:
        with open(playlist.path+'.m3u', 'w+') as f:
            for i,track in enumerate(tracks, start=1):
                if len(track.path) > 0:
                    itemPath = Path(track.path.replace('.mp4','.flac'))
                    if plexPath != '':
                        itemPath = Path(track.path.replace(settings.downloadPath, plexPath).replace('.mp4','.flac'))
                    f.write(os.path.join(itemPath)+'\n')

    except Exception as e:
        print('Error generating m3u file for playlist '+playlist.title+': '+str(e))

def generateM3u8File(settings: Settings, playlist: Playlist, tracks: list[Track]):
    plexPath = ''
    if settings.plexHomePath != '':
        plexPath = settings.plexHomePath
    try: 
        with open(playlist.path+'.m3u8', 'w+') as f:
            f.write('#EXTM3U\n')
            for i,track in enumerate(tracks, start=1):
                if len(track.path) > 0:
                    artist = getTidalArtist(track.artist)
                    if hasattr(artist, 'id'):
                        f.write(f'#EXTINF:{track.duration},{artist.name} - {track.title}\n')
                        itemPath = Path(track.path.replace('.mp4','.flac'))
                        if plexPath != '':
                            itemPath = Path(track.path.replace(settings.downloadPath, plexPath).replace('.mp4','.flac'))
                        f.write(os.path.join(itemPath)+'\n')
    except Exception as e:
        print('Error generating m3u8 file for playlist '+playlist.title+': '+str(e))