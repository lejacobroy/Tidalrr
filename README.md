<div align="center">
  <h1>Tidalrr</h1>
</div>
<p align="center">
  Tidalrr is a self-hosted service that lets you archive music tracks from Tidal, for offline listening, using a web interface.<br/>
  It can be linked with Lidarr to sync artists and albums.<br/>
  Tidalrr can also sync your Tidal Playlists to Plex & Plexamp.<br/>
  Especially usefull when going to a remote location with crappy internet but a great audio system.
</p>

## What is Tidalrr?:
Tidalrr is a complete software to keep an offline copy of your Tidal library and sychronise it every night.

By default, it will synchronise all of your playlists, but you can also import artists (and all their albums), albums, tracks and playlists from others.

The artists, albums and tracks are organized for an easy import in PlexAmp, so you can point your Tidalrr library folder to Plex.

The playlists are pushed to Plex, for offline plexAmp listening (providing that you have local access to the server running Plex)

There is a webserver to watch progression/logs and to control the software.

![image1](/assets/image.png "image1")

***

### Start everything:
I recommend that you run it using docker or docker-compose.

The image is available on [dockerhub](https://hub.docker.com/r/jacobroyquebec/tidalrr)

but I also provide an example of a docker-compose file.

Modify it and run `docker-compose up -d`

but if you want to run it barebones:

`pip install -r requirements.txt`

`python3 app.py` 

***

### First, login:
In your browser, navigate to the Tidalrr web server, http://localhost:3001

On the homepage, you should see a Tidal link to login. You must authenticate the Tidalrr app before the countdown runs out.


### Second, add a Tidal URL
Go to http://localhost:3001/actions/add and copy a Tidal URL. It can be an artist's page, an album, a track or a playlist.

All content imported this way will be queued to download automaticaly.


### Third, start the scanning process:
Note, it will start automaticaly and only run between 23:00 and 3:00 AM (configurable in the settings).

You can start it manually from the webpage: http://localhost:3001/actions/run-scans

This will scan all the Queued content (artists, albums, tracks, playlists) and extract the streaming url, preparing for the download phase.


### Fourth, download the prepared files:
Note, it will start automaticaly and only run between 3:00 and 11:00 AM (configurable in the settings).

You can start it manually from the webpage: http://localhost:3001/actions/run-downloads

This will download all the scanned urls.


***

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
- [plexPlaylistImporter](https://github.com/willowmck/plexPlaylistImporter)

## 📜 Disclaimer
- Private use only.
- Need a Tidal-HIFI subscription. 
- Do not use this method to distribute or pirate music.
- It may be illegal to use this in your country, so be informed.

