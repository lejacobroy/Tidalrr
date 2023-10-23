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
    tidalToken BLOB,
    plexUrl TEXT,
    plexToken TEXT
);

DROP TABLE IF EXISTS tidal_artists;
CREATE TABLE tidal_artists (
    id INTEGER NOT NULL PRIMARY KEY,
    name TEXT,
    url TEXT
);

DROP TABLE IF EXISTS tidal_albums;
CREATE TABLE tidal_albums (
    id INTEGER NOT NULL PRIMARY KEY,
    title TEXT,
    duration INTEGER,
    numberOfTracks INTEGER,
    numberOfVolumes INTEGER,
    releaseDate DATE,
    type  TEXT,
    version TEXT,
    cover TEXT,
    explicit BOOLEAN,
    audioQuality TEXT,
    audioModes TEXT,
    artist INTEGER,
    artists TEXT,
    url TEXT
);

DROP TABLE IF EXISTS tidal_playlists;
CREATE TABLE tidal_playlists (
    id INTEGER NOT NULL PRIMARY KEY,
    title TEXT,
    duration INTEGER,
    numberOfTracks INTEGER,
    description TEXT,
    image TEXT,
    squareImage TEXT,
    URL TEXT
);

DROP TABLE IF EXISTS tidal_tracks;
CREATE TABLE tidal_tracks (
    id INTEGER NOT NULL PRIMARY KEY,
    title TEXT,
    duration INTEGER,
    trackNumber INTEGER,
    volumeNumber INTEGER,
    trackNumberOnPlaylist INTEGER,
    version TEXT,
    isrc TEXT,
    explicit BOOLEAN,
    audioQuality TEXT,
    audioModes TEXT,
    copyRight TEXT,
    artist INTEGER,
    artists TEXT,
    album INTEGER,
    URL TEXT
);

DROP TABLE IF EXISTS tidal_queue;
CREATE TABLE tidal_queue (
    url TEXT NOT NULL PRIMARY KEY,
    type TEXT,
    login BOOLEAN,
    id INTEGER,
    path TEXT,
    encryptionKey TEXT
);

DROP TABLE IF EXISTS files;
CREATE TABLE files (
    description TEXT NOT NULL PRIMARY KEY,
    type TEXT,
    id INTEGER,
    path TEXT
);