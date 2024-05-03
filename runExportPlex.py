#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   runScans.py
@Time    :   2023/10/24
@Author  :   Jacob Roy
@Version :   1.0
@Contact :   lejacobroy@gmail.com
@Desc    :   
'''

import multiprocessing
import plexapi.exceptions
from plexapi.server import PlexServer
import re
from time import gmtime, strftime
from tidalrr.database import *
from tidalrr.workers import print_elapsed_time

# the goal of this script is to export a playlist to plex and backlink the uuid or the playlist and songs
def make_connection(baseurl: str, token: str):
    return PlexServer(baseurl, token)

def create_playlist(plex, audio, playlist:Playlist, tracks:list):
    plexPlaylist = plex.createPlaylist(playlist.title, section=audio.key, items=tracks)
    playlist.plexUUID = plexPlaylist.guid
    updateTidalPlaylist(playlist)
    print("Created playlist " + playlist.title)

def get_matching_track(plex, search_term, library_id, filename, strip_parens=False):
    try:
        results = plex.search(query=strip_appenders(search_term, strip_parens), mediatype='track', sectionId=library_id)
        if len(results) == 1:
            return results[0]
        else:
            for result in results:
                for medium in result.media:
                    for part in medium.parts:
                        if part.file == filename:
                            return result
    except plexapi.exceptions.PlexApiException as e:
        print(e)
        return None

def strip_appenders(full_title: str, strip_parens=False):
    no_prefix = strip_prefix(full_title)
    return strip_suffix(no_prefix, strip_parens)


def strip_prefix(full_title: str):
    match = re.split(r"^[0-9]*\s-", full_title)
    return match[0]

def strip_suffix(full_title: str, strip_parens=False):
    stripped_title = full_title
    start_bracket = stripped_title.find('[')
    if start_bracket > -1:
        end_bracket = stripped_title.find(']', start_bracket)
        if end_bracket > -1:
            stripped_title = stripped_title[0:start_bracket].strip()
    featuring = stripped_title.lower().find('feat.')
    if featuring > -1:
        stripped_title = stripped_title[0:featuring].strip()
    if strip_parens:
        left_paren = stripped_title.find('(')
        if left_paren > -1:
            right_paren = stripped_title.find(')', left_paren)
            if right_paren > -1:
                stripped_title = stripped_title[0:left_paren].strip()
    return stripped_title

def search_plex_for_tracks(plex, audio, playlist:Playlist):
    #f = open(m3u_file, "r")
    #lines = f.readlines()
    tracks = getTidalPlaylistTracks(playlist.uuid)
    items = []
    for track in tracks:
        if hasattr(track, 'title'):
            if len(track.plexUUID) != 0:
                try:
                    result = audio.getGuid(track.plexUUID) # .rsplit('/', 1)[1]
                    items.append(result)
                    continue
                except plexapi.exceptions.PlexApiException as e:
                    # track not found in plex by it's uuid
                    track.plexUUID = ''
                    updateTidalTrack(track)
                    #print(e)
            l: str = track.title.strip()
            if len(l) > 0:
                result = get_matching_track(plex, track.title, audio.key, l)
                if result:
                    print('Adding track ' + track.title +' to playlist '+ playlist.title)
                    track.plexUUID = result.guid
                    updateTidalTrack(track)
                    items.append(result)
                else:
                    result = get_matching_track(plex, track.title, audio.key, l, strip_parens=True)
                    if result:
                        print('Adding track ' + track.title +' to playlist '+ playlist.title)
                        track.plexUUID = result.guid
                        updateTidalTrack(track)
                        items.append(result)
                    #else:
                    #    print('ERROR: Could not find match for ' + l)
            else:
                print('DEBUG: Skipping ' + l)
    updateTidalPlaylistTracksPlexUUID(playlist.uuid)
    return items

@print_elapsed_time
def startImportPlex():
    settings = getSettings()
    if settings.plexToken != '' and settings.plexUrl != '':
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" startImportPlex")
        plex_instance = make_connection(baseurl=settings.plexUrl, token=settings.plexToken)
        audio = plex_instance.library.section('Music')
        playlists = getDownloadedTidalPlaylists()
        for i, playlist in enumerate(playlists):
            if hasattr(playlist, 'uuid'):
                # playlist has all tracks downloaded, importing to plex
                if len(playlist.plexUUID) == 0:
                    # playlist was not linked to plex
                    # check if playlist exists in plex first
                    try:
                        pplaylist = plex_instance.playlist(playlist.title)
                        playlist.plexUUID = pplaylist.guid
                        # we could use audio.getGuid(playlist.plexUUID) or on single tracks
                        updateTidalPlaylist(playlist)
                    except plexapi.exceptions.PlexApiException as e:
                        print(e)
                        # playlist title is not found in plex, create it
                        tracks = search_plex_for_tracks(plex_instance, audio, playlist)
                        if len(tracks) > 0:
                            create_playlist(plex_instance, audio, playlist, tracks)
                else:
                    # we need to update the playlist
                    print('Playlist '+ playlist.title +' already linked to plex, updating...')
                    pplaylist = plex_instance.playlist(playlist.title)
                    plexTracks = pplaylist.items()
                    tidalTracks = getTidalPlaylistTracks(playlist.uuid)
                    newTracks = []
                    removeTracks = []
                    #compare tracks in both systems
                    for plexTrack in plexTracks:
                        plexCheck = False
                        for tidalTrack in tidalTracks:
                            if len(tidalTrack.plexUUID) > 0:
                                if plexTrack.guid == tidalTrack.plexUUID:
                                    plexCheck = True
                        if not plexCheck:
                            # plexTrack was not found in tidalPlaylist 
                            removeTracks.append(plexTrack)

                    for tidalTrack in tidalTracks:
                        tidalCheck = False
                        for plexTrack in plexTracks:
                            if len(tidalTrack.plexUUID) > 0 :
                                if tidalTrack.plexUUID == plexTrack.guid:
                                    tidalCheck = True
                            else:
                                if tidalTrack.title == plexTrack.title:
                                    # we need to add the new track to plex somehow
                                    # then retreive the guid
                                    # then change this flag to True
                                    tidalCheck = False
                        if not tidalCheck and len(tidalTrack.plexUUID) > 0 :
                            # tidalTrack was not found in plexPlaylist
                            try:
                                #correspondingPlexTrack = tidalTrack.plexUUID
                                # apparently, getGuid dosen't work for audio
                                newTracks.append(tidalTrack.plexUUID)
                                # since we can'T do that, we could delete the plexPlaylist and recreate it instead
                            except plexapi.exceptions.PlexApiException as e:
                                print(e)
                                # track not found in plex, add it

                    # add new tracks with pplaylist.addItems(audio.getGuid(track.plexUUID))
                    if len(newTracks) > 0:
                        #pplaylist.addItems(newTracks)
                        #print('Added '+ str(len(newTracks)) +' new tracks to plex playlist '+ playlist.title)
                        pplaylist.delete()
                        tracks = search_plex_for_tracks(plex_instance, audio, playlist)
                        if len(tracks) > 0:
                                create_playlist(plex_instance, audio, playlist, tracks)
                        print('Recreated playlist '+ playlist.title)
                    
                    # remove tracks with plexPlaylist.removeItems(plexTrack)
                    if len(removeTracks) > 0:
                        pplaylist.removeItems(removeTracks)
                        print('Removed '+ str(len(newTracks)) +' tracks to plex playlist '+ playlist.title)


def forkImportPlex():
    # Start foo as a process
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" Starting startImportPlex")
    p = multiprocessing.Process(target=startImportPlex)
    p.start()

    p.join()

    # If thread is active
    if p.is_alive():
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" ImportPlex are running... let's kill it...")
        # Terminate foo
        p.terminate()
        # Cleanup
        p.join()

if __name__ == '__main__':
    forkImportPlex()
    #main()
    #mainSchedule()