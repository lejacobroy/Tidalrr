<div align="center">
  <h1>Tidalrr</h1>
</div>
<p align="center">
  Tidalrr is a self-hosted service that lets you download music tracks from Tidal.<br/>
  It can be interfaced with Lidarr to sync Artists, Albums, Playlists, etc. using the Lidarr integration.<br/>
  Tidalrr can also sync your Tidal Playlists to Plex & Plexamp.
</p>

## How to use:
### Download content from a Tidal URL
`tidalrr --url URL` 

### Download album by a title
``tidalrr --album 'Artist Name - Album Title'` 

### Download content from a file containing Tidal links (songs, albums, playlists, etc)
`tidalrr --file urls.txt` , where each link is on a new line in the urls.txt file.

### Query Lidarr's wanted list of albums and downloads them from Tidall
``tidalrr --lidarr` . Note that for now, the matching algorithm is pretty strict and needs a perfect match for both the artist's name and the album's title.

### Downloads all of the Tidal user's playlists
`tidalrr --syncplaylists` 

### Inject downloaded Tidal playlists (.m3u8 files) into the Spark app
`tidalrr --inject`  WARNING: you should not use this, as it can corrupt your Spark database.

While it's available in a docker image, there's currently no way to execute the different options except by connecting directly to the container.

## Todo:
- ✅ refactor and cleanup code
- ✅ remove video support
- ✅ configureable highest quality
- ✅ migrate interactive settings to a json config file
- ✅ migrate interactive settings to CLI arguments
- ✅ download content from a file list of links (great for playlists)
- ✅ query Lidarr wanted list of albums and downloads them
- ✅ Sync all user's playlists
- ✅ package it in a docker container [Dockerhub](https://hub.docker.com/r/jacobroyquebec/tidalrr)
- ✅ generate .m3u and .m3u8 playlist files
- ✅ migrate json config file to sqlite db
- ✅ add files to a queue and download them using a separate worker thread
- remove duplicated functions and refactor files
- more work on the Queues
    - add artists
    - add albums
    - add lyrics
    - download covers
- how to know what is missing/downloaded compared to tidal?
- replace and select Masters albums/track
    - store matching information in db for future use
- replace classes with functions as it's not needed and makes the code less readable
    - language.py
    - tidal.py
    - settings.py
    - model.py
- create and sync Plex Playlist from Tidal Playlists (using PPP)
- create an api webserver and control center
    - Read-only mode for now
    - start jobs
    - add urls to the queue from tidal search, urls or files (replace cli)
- split monolith into workers with cron jobs
- Inject Tidal playlist into Spark by Devialet (using spark.py it can inject in the DB, but spark does not recognise/use it yet)
- local ai matching pattern

## 🎨 Libraries and reference

- [aigpy](https://github.com/yaronzz/AIGPY)
- [python-tidal](https://github.com/tamland/python-tidal)
- [redsea](https://github.com/redsudo/RedSea)
- [tidal-wiki](https://github.com/Fokka-Engineering/TIDAL/wiki)
- [tidal-dl](https://github.com/yaronzz/Tidal-Media-Downloader)
- [lidarr API](https://lidarr.audio/docs/api/#/)
- [PPP](https://github.com/XDGFX/PPP)
- [tidal-m3u](https://github.com/jocap/tidal-m3u/blob/master/m3u.py)
- [bootstrap-flask](https://github.com/helloflask/bootstrap-flask)

## 📜 Disclaimer
- Private use only.
- Need a Tidal-HIFI subscription. 
- Do not use this method to distribute or pirate music.
- It may be illegal to use this in your country, so be informed.

## Usage
I recommend that you run it using docker or docker-compose.
The image is available on [dockerhub](https://hub.docker.com/r/jacobroyquebec/tidalrr)
but I also provide an example of a docker-compose file.
Modify it and run `docker-compose up -d`

To use, watch the docker logs to capture the login URL and authenticate your tidalrr instance to Tidal.

## Developing

```shell
./build.sh
```

