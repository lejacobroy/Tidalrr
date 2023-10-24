import os
import sqlite3

"""Sync an m3u8 playlist to the Spark db
    1. Check if the playlist exists
        a. If it does, remove all items rows
        b. Else create the playlist row
    2. Insert all rows
"""

connection = sqlite3.connect("spark/collection.db")
playlist_file = 'spark/test.m3u8'
playlist_name = 'My Playlist'
playlist_items = []

with open(playlist_file, 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('#EXTINF:'):
            duration, title = line[8:].split(',', 1)
            item = {'title': title.strip(), 'duration': duration.strip()}
            playlist_items.append(item)
        elif line.startswith('#') or not line:
            continue
        else:
            playlist_items[-1]['url'] = line.strip()

cursor = connection.cursor()
# verify that the playlist exists
playlists = cursor.execute(f"Select id from playlist where name = '{playlist_name}'").fetchall()

if len(playlists) == 0:
    # SQL query to insert into playlist table
    playlist_query = f"INSERT INTO playlist (id, engine_type, hash, last_update, name, is_favorite, is_podcast) VALUES (1,1,'{playlist_name}', DATE(), '{playlist_name}',0,0);"
    print(playlist_query)
    cursor.execute(playlist_query)
    playlists = cursor.execute(f"Select id from playlist where name = '{playlist_name}'").fetchall()


for i, item in enumerate(playlist_items):
    # SQL query to get the track_id from a path file
    track = cursor.execute(f"SELECT id FROM track WHERE url = '{item['url']}'").fetchall()
    track_query = f"INSERT INTO playlist_link (id, playlist_id, track_id) VALUES ({i}, {playlists[0][0]}, {track[0][0]});"
    cursor.execute(track_query)

#cursor.execute(playlist_items_query)
connection.commit()
# Print SQL queries for debugging
#print(playlist_query)
#print(playlist_items_query)

def injectPlaylist(playlistPath):
    # use spark.py function to load the .m3u8 file into Spark DB
    # spark DB is located at '~/Library/Applications Support/Devialet/Spakr/Collection.db'
    print('Validating m3u8 playlist...')
    # read .m3u8
        # is valid, make a copy of the db with the date
    print('Valid m3u8, DB backup.')
        # inject the playlist
    print('Injected playlist X into Spark.')