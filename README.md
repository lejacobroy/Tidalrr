<div align="center">
  <h1>Tidalrr</h1>
</div>
<p align="center">
  Tidalrr is a self-hosted service that lets you download music tracks from Tidal.<br/>
  It can be interfaced with Lidarr to sync Artists, Albums, Playlists, etc. using the Lidarr integration.<br/>
  Tidalrr can also sync your Tidal Playlists to Plex & Plexamp.
</p>

## Todo:
- ✅ refactor and cleanup code
- ✅ remove video support
- ✅ configureable highest quality
- ✅ migrate interactive settings to a json config file
- ✅ migrate interactive settings to CLI arguments
- ✅ download content from a file list of links (great for playlists)
- ✅ query Lidarr wanted list of albums and downloads them
- Sync all user's playlists
- generate .pls and .m3u8 playlist files
- create and sync Plex Playlist from Tidal Playlists
- create an api webserver that can be used with Lidarr
- package it in a docker container

## 🎨 Libraries and reference

- [aigpy](https://github.com/yaronzz/AIGPY)
- [python-tidal](https://github.com/tamland/python-tidal)
- [redsea](https://github.com/redsudo/RedSea)
- [tidal-wiki](https://github.com/Fokka-Engineering/TIDAL/wiki)
- [tidal-dl](https://github.com/yaronzz/Tidal-Media-Downloader)
- [lidarr API](https://lidarr.audio/docs/api/#/)

## 📜 Disclaimer
- Private use only.
- Need a Tidal-HIFI subscription. 
- Do not use this method to distribute or pirate music.
- It may be illegal to use this in your country, so be informed.

## Developing

```shell
pip3 uninstall tidal-dl
pip3 install -r requirements.txt --user
python3 setup.py install
```

