## Todo:
- Inject Tidal playlist into Spark by Devialet (using spark.py it can inject in the DB, but spark does not recognise/use it yet)
- local ai matching pattern
- more work on the Queues
    - scan files
- replace and select Masters albums/track
    - store matching information in db for future use (superseeded)
    - when scanning a track, look if it's album is superseeded, then scan the corresponding track
    - superseeded table? - for albums and tracks
- create an api webserver and control center
    - sync lidarr
        - interactive match with search
    - inject spark
    - backlink playlists from plex
    - maintenance
        - albums with master or max available to upgrade
        - incomplete albums, artists, playlists
        - missing covers
        - missing lyrics
        - migrate paths in queues and files

scan playlist mark as downloaded
scan & download tracks artists name too long
