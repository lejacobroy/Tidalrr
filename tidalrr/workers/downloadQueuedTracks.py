#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   workerDownload.py
@Time    :   2023/10/23
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''
#import aigpy
import time
import ffmpeg
from os.path import exists
from tidalrr.paths import *
from tidalrr.decryption import *
from tidalrr.tidal import *
from urllib.parse import urlparse
from urllib.parse import parse_qs
from tidalrr.workers import *
from tidalrr.workers.scanQueuedTracks import scanTrack
import logging

logger = logging.getLogger(__name__)

def refreshStreamURL(id=int, audioQuality=str):
    return TIDAL_API.getStreamUrl(id, audioQuality)

def isNeedRefresh(url):
    #extract the 'expire' key from the url
    parsed_url = urlparse(url)
    if not hasattr(parse_qs(parsed_url.query), 'Expires'):
        return True
    else:
        captured_value = parse_qs(parsed_url.query)['Expires'][0]
        if int(captured_value) > int( time.time() ):
            return False
        return True

def workDownloadTrack(queue = Queue, track=Track):
    album = getTidalAlbum(track.album)
    artist = getTidalArtist(album.artist)
    result = True
    if album is not None and artist is not None:
        settings = getSettings()
        if queue.login and isNeedRefresh(queue.url):
            print('Refreshing URL '+ track.title)
            temp = refreshStreamURL(queue.id, settings.audioQuality)
            if hasattr(temp, 'url'):
                queue.url = temp.url
                queue.encryptionKey = temp.encryptionKey
                queue.urls = json.dumps(temp.urls)
                print('Refreshed URL '+ track.title)
            else:
                print('Cant get URL', temp)
                #completeURL refresh
                scanTrack(track, album, settings.audioQuality)
                result = False

        # check exist
        if not isSkip(queue.path, queue.url) and result:
            # download
            #logging.info("[DL Track] name=" + aigpy.path.getFileName(queue.path) + "\nurl=" + queue.url)
            sleep_time = random.randint(500, 5000) / 1000
            #print(f"Sleeping for {sleep_time} seconds, to mimic human behaviour and prevent too many requests error")
            time.sleep(sleep_time)

            #tool = aigpy.download.DownloadTool(queue.path + '.part', json.loads(queue.urls))
            #tool.setPartSize(partSize)
            #check, err = tool.start(False)
            check, err = download_and_combine(queue.path, json.loads(queue.urls))
            if not check:
                print(f"DL Track[{track.title}] failed.")
                print(json.dumps(err))
                result = False
            if result and check:
                # encrypted -> decrypt and remove encrypted file
                encrypted(queue.encryptionKey, queue.path, queue.path)

                if '.mp4' in queue.path:
                    # convert .mp4 back to .flac
                    final_path = queue.path.rsplit(".", 1)[0] + '.flac'
                    print(final_path)
                    try:
                        ffmpeg.input(queue.path, hide_banner=None, y=None).output(final_path, acodec='copy',
                                                                                            loglevel='error').run()
                        # Remove all files
                        os.remove(queue.path)
                        queue.path = final_path
                    except:
                        print('FFmpeg is not installed or working! Using fallback, may have errors')
                        result = False
                        return result

                # contributors
                try:
                    contributors = TIDAL_API.getTrackContributors(track.id)
                except:
                    contributors = None

                # lyrics
                try:
                    lyrics = TIDAL_API.getLyrics(track.id).subtitles
                    if settings.lyricFile:
                        lrcPath = queue.path.rsplit(".", 1)[0] + '.lrc'
                        aigpy.file.write(lrcPath, lyrics, 'w')
                except:
                    lyrics = ''
                
                metadataArtist = [str(artist.name)]
                metadataArtists = [str(album.artists)]
                print('Downloaded file', track.title, track.audioQuality, queue.path)
                try:
                    setMetaData(track, album, metadataArtist, metadataArtists, queue.path, contributors, lyrics)
                    result = True
                except:
                    print('cannot write to flac')
                    result = False
                #print(str(number)+ " : " + artist.name + " - " + album.title + " - " + track.title)
                #print(str(number)+ " : " +aigpy.path.getFileName(path) + " (skip:already exists!)")
    else:
        print('No artist or album')
        result = False
    return result


def downloadQueuedTracks():
    try:
        tidalrrStart()
        
        queue_items = getTidalQueues('Track')
        for i, queue in enumerate(queue_items):
            try:
                file = getFileById(queue.id)
                track = getTidalTrack(queue.id)
                
                if file is None:
                    if not exists(track.path):
                        print('Downloading track file', str(i)," / ", str(len(queue_items)), track.title)
                        track.downloaded = workDownloadTrack(queue, track)
                        
                    if track.downloaded:
                        # save file in db
                        file = File(
                            description=track.title,
                            type='Track',
                            id=track.id,
                            path=queue.path
                        )
                        addFiles(file)

                        # remove queue in db
                        delTidalQueue(queue.path)

                        # update track row
                        track.path = queue.path
                        track.queued = False
                        track.downloaded = True
                        updateTidalTrack(track)
            except Exception as e:
                print("Error downloading track : ", track.title, e)

        # update downloaded albums & artists
        updateTidalAlbumsDownloaded()
        updateTidalArtistsDownloaded()
        updateTidalPlaylistsDownloaded()
        
    except Exception as e:
        print("Error in downloadQueuedTracks: ", e)

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

    combine_file_parts(path, *file_parts)
    # Clean up: delete individual file parts
    for file_part in file_parts:
        try:
            os.remove(file_part)
            logging.info(f'Deleted file part: {file_part}')
        except Exception as e:
            logging.error(f'Error deleting file part {file_part}: {e}')
            return False, str(e)
    return True, err