## Todo:
- Inject Tidal playlist into Spark by Devialet (using spark.py it can inject in the DB, but spark does not recognise/use it yet)
- local ai matching pattern

- replace and select Masters albums/track
    - store matching information in db for future use (superseeded)
    - when scanning a track, look if it's album is superseeded, then scan the corresponding track
    - superseeded table? - for albums and tracks

- create an api webserver and control center
    - inject spark
    - maintenance
        - albums with master or max available to upgrade
        - incomplete albums, artists, playlists
        - missing covers
        - missing lyrics
        - migrate paths in queues and files

- delete and recreate playlists to add tracks

- change logs to % completions with time estimation