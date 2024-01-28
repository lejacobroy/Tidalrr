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

def scanQueuedTracks():
    tracks = getQueuedTidalTracks()
    if len(tracks) > 0:
        for i, track in enumerate(tracks):
            try:
                if hasattr(track, 'id'):
                    print('Scanning track ', str(i), ' / ',str(len(tracks)), track.title)
                    track = start_track(track)
                    updateTidalTrack(track)

                    # update downloaded albums & artists
                    updateTidalAlbumsDownloaded()
                    updateTidalArtistsDownloaded()
                    updateTidalPlaylistsDownloaded()
            except Exception as e:
                print("Error scanning track: ", e)
                if "Track" in str(e) and "not found" in str(e):
                    track.queued = False
                    updateTidalTrack(track)
                if "Asset is not ready for playback" == str(e):
                    track.queued = True
                    updateTidalTrack(track)
        updatePlaylistsFiles()

def start_track(track: Track):
    if exists(track.path):
        track = setDownloaded(track, True)
        saveFileFromTrack(track)
        return track
    if getFileById(track.id) is not None:
        # fs file is not preset, but db file is, let's clear it
        delFile(track.id)
        track = setDownloaded(track, False)

    settings = getSettings()

    try:
        artist = getTidalArtist(track.artist)
        if not hasattr(artist, 'id'):
            # insert artist in db, unmonitored
            addTidalArtist(TIDAL_API.getArtist(track.artist))
    except Exception as e:
        print("Error adding artist: ", e)
        track = setDownloaded(track, False)
        return track
    try:    
        album = getTidalAlbum(track.album)
        if not hasattr(album, 'id'):
            # insert artist in db, unmonitored
            addTidalAlbum(TIDAL_API.getAlbum(track.album))
        else: 
            if settings.saveCovers:
                scanCover(album)
    except Exception as e:
        print("Error adding album: ", e)
        track = setDownloaded(track, False)
        return track

    try:
        track = downloadTrack(settings, track, artist, album)
    except Exception as e:
        print("Error downloading track: ", e)
        track = setDownloaded(track, False)
        return track

    if track.downloaded:
        print('Downloaded track file', track.title)
        saveFileFromTrack(track)
        track = setDownloaded(track, True)
        return track

def downloadTrack(settings=Settings, track=Track, artist= Artist, album= Album):
    stream, track.path = scanTrackPath(track, album, None)
    # check exist
    if track.path is None or isSkip(track.path, track.url) or stream is None or len(stream.urls) == 0:
        # track dosen't exists on tidal or should be skipped
        track = setDownloaded(track, False)
        return track

    # download
    sleep_time = random.randint(500, 5000) / 1000
    time.sleep(sleep_time)
    
    check, err = download_and_combine(track.path, stream.urls)
    if not check:
        print(f"DL Track[{track.title}] failed.")
        print(json.dumps(err))
        track = setDownloaded(track, False)
        return track

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
            track = setDownloaded(track, False)
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
    except:
        print('cannot write to flac')
        track = setDownloaded(track, False)
        return track
    track = setDownloaded(track, True)
    return track

def scanTrackPath(track=Track, album=Album, playlist=Playlist):
    path = ''
    settings = getSettings()
    stream = StreamUrl()
    try:
        stream = TIDAL_API.getStreamUrl(track.id, settings.audioQuality) 
    except Exception as e:
        print("Error getting stream URL: ", e)
        if str(e) == "Asset is not ready for playback":
            return None, None
        if str(e) == "The token has expired. (Expired on time)":
            loginByConfig()
            return None, None

    artist = getTidalArtist(track.artist)
    if artist is None:
        try:
            artist = TIDAL_API.getArtist(track.artist)
            addTidalArtist(artist)
        except Exception as e:
            print("Error getting artist: ", e)

    albumArtist = getTidalArtist(album.artist)
    if albumArtist is None:
        try:
            albumArtist = TIDAL_API.getArtist(album.artist)
            addTidalArtist(albumArtist)
        except Exception as e:
            print("Error getting album artist: ", e)

    if artist is not None and stream is not None and stream.url is not None:
        try:
            path = getTrackPath(track, stream, artist, album, playlist)
        except Exception as e:
            print("Error getting track path: ", e)
            return None, None

    return stream, path

def saveFileFromTrack(track: Track):
    # save file in db
    file = File(
        description=track.title,
        type='Track',
        id=track.id,
        path=track.path
    )
    addFiles(file)

def setDownloaded(track: Track, downloaded: bool):
    if downloaded:
        track.downloaded = True
        track.queued = False
    else:
        track.downloaded = False
        track.queued = True

    return track
