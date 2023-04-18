import os
import sqlite3

"""Sync an m3u8 playlist to the Spark db
    1. Check if the playlist exists
        a. If it does, remove all items rows
        b. Else create the playlist row
    2. Insert all rows
"""

connection = sqlite3.connect("collection.db")
playlist_file = 'test.m3u8'
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

# Print playlist_items for debugging
print(playlist_items)

# SQL query to insert into playlist table
playlist_query = f"INSERT INTO playlist (name) VALUES ('{playlist_name}');"

cursor = connection.cursor()
cursor.execute(playlist_query)

for i, item in enumerate(playlist_items):
    # SQL query to get the track_id from a path file
    track_query = f"(SELECT id FROM track WHERE url = '{item['url']}')"
    print(track_query)
    playlist_items[i]['track_id'] = track_query

# SQL query to insert into playlist_items table
playlist_items_query = "INSERT INTO playlist_items (playlist_id, title, duration, track_id) VALUES "
values = []
for i, item in enumerate(playlist_items):
    values.append(f"(1, '{item['title']}', '{item['duration']}', {item['track_id']})")
playlist_items_query += ','.join(values) + ';'

cursor.execute(playlist_items_query)

# Print SQL queries for debugging
print(playlist_query)
print(playlist_items_query)
