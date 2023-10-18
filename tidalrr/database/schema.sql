DROP TABLE IF EXISTS settings;

CREATE TABLE settings (
    albumFolderFormat TEXT NOT NULL,
    apiKeyIndex INTEGER,
    audioQuality TEXT,
    checkExist BOOLEAN,
    downloadDelay BOOLEAN,
    downloadPath TEXT,
    includeEP BOOLEAN,
    language INTEGER,
    lyricFile BOOLEAN,
    multiThread BOOLEAN,
    playlistFolderFormat TEXT NOT NULL,
    saveAlbumInfo BOOLEAN,
    saveCovers BOOLEAN,
    showProgress BOOLEAN,
    showTrackInfo BOOLEAN,
    trackFileFormat TEXT NOT NULL,
    usePlaylistFolder BOOLEAN,
    lidarrUrl TEXT,
    lidarrApi TEXT,
    tidalToken TEXT,
    plexUrl TEXT,
    plexToken TEXT
)