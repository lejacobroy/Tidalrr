<div align="center">
  <h1>Tidalrr</h1>
</div>
<p align="center">
  Tidalrr is a self-hosted service that lets you archive music tracks from Tidal, for offline listening, using a web interface.<br/>
  It can be linked with Lidarr to sync artists and albums using the Lidarr integration.<br/>
  Tidalrr can also sync your Tidal Playlists to Plex & Plexamp.<br/>
  Especially usefull when going to a remote location with crappy internet but a great audio system.
</p>

## How to use:
Tidalrr is a complete software to keep an offline copy of your Tidal library and sychronise it every night.
By default, it will synchronise all of your playlists, but you can also import artists (and all their albums), albums, tracks and playlists from others.
The artists, albums and tracks are organized for an easy import in PlexAmp, so you can point your library folder to Plex.
The playlists are pushed to Plex, for offline plexAmp listening (providing that you have local access to the server running Plex)
There is a webserver to watch progression and control the software.

## to enable Plex playlist sync
Clone [plexPlaylistImporter](https://github.com/willowmck/plexPlaylistImporter) into Tidalrr/PPI

### Start everything:
`pip install -r requirements.txt``
`python3 app.py` 
OR
`docker-compose up -d` 

### First, import some URLs from a text file:
Go to http://localhost:3001/actions/uploadUrlsFile
And upload a text file containing URLs to scan.
All content imported this way will be queued to download automaticaly.

### Second, start the scanning process:
Note, it will start automaticaly and only run between 12:00 and 6:00 AM.
You can start is manually from the webpage: http://localhost:3001/actions/run-scans
This will scan all the Queued content (artists, albums, tracks, playlists) and extract the download url, preparing for the download phase.

### Third, download the prepared files:
Note, it will start automaticaly and only run between 12:00 and 6:00 AM.
You can start is manually from the webpage: http://localhost:3001/actions/run-downloads
This will download all the scanned urls.

### Query Lidarr's wanted list of albums and downloads them from Tidal
``tidalrr --lidarr` . Note that for now, the matching algorithm is pretty strict and needs a perfect match for both the artist's name and the album's title.

### Inject downloaded Tidal playlists (.m3u8 files) into the Spark app
`tidalrr --inject`  WARNING: you should not use this, as it can corrupt your Spark database.

While it's available in a docker image, there's currently no way to execute the different options except by connecting directly to the container.

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

