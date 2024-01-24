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
from tidalrr.database import *
from tidalrr.tidal import *
from tidalrr.workers import *
import logging

logger = logging.getLogger(__name__)

def workDownloadTrack(track=Track):
    album = getTidalAlbum(track.album)
    artist = getTidalArtist(album.artist)
    if album is not None and artist is not None:
        settings = getSettings()
        
        stream, track.path = scanTrackPath(track, album, None)
        # check exist
        if not isSkip(track.path, track.url):
            # download
            sleep_time = random.randint(500, 5000) / 1000
            time.sleep(sleep_time)

            check, err = download_and_combine(track.path, stream.urls)
            if not check:
                print(f"DL Track[{track.title}] failed.")
                print(json.dumps(err))
                track.downloaded = False
                return track
            if check:
                # encrypted -> decrypt and remove encrypted file
                encrypted(stream.encryptionKey, track.path, track.path)

                if '.mp4' in track.path:
                    # convert .mp4 back to .flac
                    final_path = track.path.rsplit(".", 1)[0] + '.flac'
                    #print(final_path)
                    try:
                        ffmpeg.input(track.path, hide_banner=None, y=None).output(final_path, acodec='copy',
                                                                                            loglevel='error').run()
                        # Remove all files
                        os.remove(track.path)
                        track.path = final_path
                    except:
                        print('FFmpeg is not installed or working! Using fallback, may have errors')
                        track.downloaded = False
                        return track

                # contributors
                try:
                    contributors = TIDAL_API.getTrackContributors(track.id)
                except:
                    contributors = None

                # lyrics
                try:
                    lyrics = TIDAL_API.getLyrics(track.id).subtitles
                    if settings.lyricFile:
                        lrcPath = track.path.rsplit(".", 1)[0] + '.lrc'
                        aigpy.file.write(lrcPath, lyrics, 'w')
                except:
                    lyrics = ''
                
                metadataArtist = [str(artist.name)]
                metadataArtists = [str(album.artists)]
                try:
                    setMetaData(track, album, metadataArtist, metadataArtists, track.path, contributors, lyrics)
                    track.downloaded = True
                except:
                    print('cannot write to flac')
                    track.downloaded = False
    else:
        print('No artist or album')
        track.downloaded = False
    return track


def downloadTrack(track=Track):
    try:
        if not exists(track.path):
            print('Downloading track file', track.title)
            track = workDownloadTrack(track)
        else:
            track.downloaded = True
            
        if track.downloaded:
            # save file in db
            file = File(
                description=track.title,
                type='Track',
                id=track.id,
                path=track.path
            )
            addFiles(file)

            # remove queue in db
            delTidalQueue(track.id)

        updateTidalTrack(track)

        # update downloaded albums & artists
        updateTidalAlbumsDownloaded()
        updateTidalArtistsDownloaded()
        updateTidalPlaylistsDownloaded()
    except Exception as e:
        print("Error in downloadTrack: ", e)

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

def scanQueuedTracks():
    try:
        tracks = getTidalTracks()
        if len(tracks) > 0:
            for i, track in enumerate(tracks):
                try:
                    if hasattr(track, 'id') and track.queued:
                        print('Scanning track ', str(i), ' / ',str(len(tracks)), track.title)
                        result = start_track(track)
                        if result:
                            track.queued = False
                            updateTidalTrack(track)
                except Exception as e:
                    print("Error scanning track: ", e)
                    if "Track" in str(e) and "not found" in str(e):
                        track.queued = False
                        updateTidalTrack(track)
                    if "Asset is not ready for playback" == str(e):
                        track.queued = True
                        updateTidalTrack(track)
    except Exception as e:
        print("Error getting tracks: ", e)

def start_track(obj: Track):
    try:
        settings = getSettings()
        try:
            if not hasattr(getTidalArtist(obj.artist), 'id'):
                # insert artist in db, unmonitored
                addTidalArtist(TIDAL_API.getArtist(obj.artist))
        except Exception as e:
            print("Error adding artist: ", e)
            
        try:    
            #same for album
            if not hasattr(getTidalAlbum(obj.album), 'id'):
                # insert artist in db, unmonitored
                addTidalAlbum(TIDAL_API.getAlbum(obj.album))
        except Exception as e:
            print("Error adding album: ", e)

        try:
            album = getTidalAlbum(obj.album)
            if settings.saveCovers:
                scanCover(album)
        except Exception as e:
            print("Error getting album: ", e)

        try:
            file = getFileById(obj.id)
            queue = getTidalQueueById(obj.id)
            if file is None and queue is None:
                return downloadTrack(obj)
                #return scanTrack(obj, album)
            else:
                print('File exists, skipping')
                return True
        except Exception as e:
            print("Error scanning track: ", e)
    except Exception as e:
        print("Error in scan queued tracks: ", e)

def scanTrackPath(track=Track, album=Album, playlist=Playlist):
    path = ''
    try:
        settings = getSettings()
    except Exception as e:
        print("Error getting settings: ", e)
    stream = StreamUrl()
    try:
        stream = TIDAL_API.getStreamUrl(track.id, settings.audioQuality) 
    except Exception as e:
        print("Error getting stream URL: ", e)
        if str(e) == "Asset is not ready for playback":
            return None, None

    try:
        artist = getTidalArtist(track.artist)
        if artist is None:
            try:
                artist = TIDAL_API.getArtist(track.artist)
                addTidalArtist(artist)
            except Exception as e:
                print("Error getting artist: ", e)
    except Exception as e:
        print("Error getting tidal artist: ", e)

    try:
        albumArtist = getTidalArtist(album.artist)
        if albumArtist is None:
            try:
                albumArtist = TIDAL_API.getArtist(album.artist)
                addTidalArtist(albumArtist)
            except Exception as e:
                print("Error getting album artist: ", e)
    except Exception as e:
        print("Error getting tidal album artist: ", e)

    if artist is not None and stream is not None and stream.url is not None:
        try:
            path = getTrackPath(track, stream, artist, album, playlist)
        except Exception as e:
            print("Error getting track path: ", e)

    return stream, path