<div align="center">
  <h1>Tidalrr</h1>
</div>
<p align="center">
  Tidalrr is a self-hosted service that lets you download music tracks from Tidal. It can be interfaces with Lidarr to sync Artists, Albums, Playlists, etc.
  Tidalrr can also re-create your Tidal Playlists in Plex & Plexamp.
</p>

Todo:
    - refactor and cleanup code
    - remove video support
    - configureable highest quality
    - migrate interactive settings to a json config file and CLI arguments
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

## 📜 Disclaimer
- Private use only.
- Need a Tidal-HIFI subscription. 
- You should not use this method to distribute or pirate music.
- It may be illegal to use this in your country, so be informed.

## Developing

```shell
pip3 uninstall tidal-dl
pip3 install -r requirements.txt --user
python3 setup.py install
```

