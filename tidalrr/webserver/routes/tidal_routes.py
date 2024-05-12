from flask import Blueprint, render_template
from tidalrr.database.tracks import getTidalTracks, getTidalTrack, getTracksForAlbum, updateTidalTrack
from tidalrr.database.albums import getTidalAlbum, getTidalAlbums,getAlbumsForArtist, updateTidalAlbum, getNumDownloadedAlbumTracks
from tidalrr.database.artists import getTidalArtist, updateTidalArtist, getTidalArtists, getNumArtistAlbums, getNumDownloadedArtistAlbums
from tidalrr.database.playlists import getTidalPlaylist, getTidalPlaylists, getTidalPlaylistTracks, getNumDownloadedPlaylistTracks, updateTidalPlaylist
from tidalrr.database.queues import isIdInQueue, delTidalQueue
tidal_bp = Blueprint('tidal', __name__)

@tidal_bp.route("/artists")
def tidalArtists():
    artists = getTidalArtists()
    for artist in artists:
        artist.numAlbums = getNumArtistAlbums(artist.id)
        artist.numDownloadedAlbums = getNumDownloadedArtistAlbums(artist.id) 
        artist.inQueue = isIdInQueue(artist.id)
    return render_template("tidal/artists.html", artists = artists)

@tidal_bp.route("/artist/<int:id>")
def viewArtist(id):
    artist = getTidalArtist(id)
    artist.inQueue = isIdInQueue(artist.id)
    artist.numAlbums = getNumArtistAlbums(artist.id)
    artist.numDownloadedAlbums = getNumDownloadedArtistAlbums(artist.id) 
    albums = getAlbumsForArtist(id)
    for album in albums:
        album.numDownloadedTracks = getNumDownloadedAlbumTracks(album.id)

    return render_template("tidal/artist.html", artist=artist, albums=albums)

@tidal_bp.route("/artist/<int:id>/monitor", methods=['POST'])  
def monitorArtist(id):
    artist = getTidalArtist(id)
    artist.monitored = True
    updateTidalArtist(artist)
    return "OK"

@tidal_bp.route("/artist/<int:id>/unmonitor", methods=['POST'])  
def unqueueArtist(id):
    artist = getTidalArtist(id)
    artist.monitored = False
    updateTidalArtist(artist)
    return "OK"

# Album routes
@tidal_bp.route("/album/<int:id>")
def viewAlbum(id):
  album = getTidalAlbum(id)
  album.inQueue = isIdInQueue(album.id)
  album.numDownloadedTracks = getNumDownloadedAlbumTracks(album.id)
  tracks = getTracksForAlbum(id)
  for track in tracks:
    track.albumTitle = album.title

  return render_template("tidal/album.html", album=album, tracks=tracks)

@tidal_bp.route("/album/<int:id>/monitor", methods=['POST'])
def queueAlbum(id):
  album = getTidalAlbum(id)
  album.monitored = True
  updateTidalAlbum(album)
  
  return "OK"

@tidal_bp.route("/album/<int:id>/unmonitor", methods=['POST'])
def unqueueAlbum(id):
  album = getTidalAlbum(id)
  album.monitored = False
  updateTidalAlbum(album)

  delTidalQueue(album.id)

  return "OK"

@tidal_bp.route("/albums") 
def tidalAlbumsPaged():

  albums = getTidalAlbums()

  for album in albums:
    album.inQueue = isIdInQueue(album.id)
    album.numDownloadedTracks = getNumDownloadedAlbumTracks(album.id)

  return render_template("tidal/albums.html", albums=albums)

# Playlist routes  
@tidal_bp.route("/playlist/<uuid>")
def viewPlaylist(uuid):
  playlist = getTidalPlaylist(uuid)
  playlist.inQueue = isIdInQueue(playlist.uuid)
  playlist.numDownloadedTracks = getNumDownloadedPlaylistTracks(playlist.uuid)
  tracks = getTidalPlaylistTracks(uuid)
  for track in tracks:
    track.albumTitle = getTidalAlbum(track.album).title
    track.inQueue = isIdInQueue(track.id)

  return render_template("tidal/playlist.html", playlist=playlist, tracks=tracks)

@tidal_bp.route("/playlist/<uuid>/monitor", methods=['POST'])
def queuePlaylist(uuid):
  playlist = getTidalPlaylist(uuid)
  playlist.monitored = True
  updateTidalPlaylist(playlist)

  return "OK"
  
@tidal_bp.route("/playlist/<uuid>/unmonitor", methods=['POST'])
def unqueuePlaylist(uuid):
  playlist = getTidalPlaylist(uuid)
  playlist.monitored = False
  updateTidalPlaylist(playlist)

  return "OK"

@tidal_bp.route("/playlists") 
def tidalPlaylists():

  playlists = getTidalPlaylists()

  for playlist in playlists:
    playlist.inQueue = isIdInQueue(playlist.uuid)
    playlist.numDownloadedTracks = getNumDownloadedPlaylistTracks(playlist.uuid)

  return render_template("tidal/playlists.html", playlists=playlists)


# Track routes
@tidal_bp.route("/track/<int:id>")
def viewTrack(id):
  track = getTidalTrack(id)
  track.inQueue = isIdInQueue(track.id)
  album = getTidalAlbum(track.album)
  artist = getTidalArtist(track.artist)

  return render_template("tidal/track.html", track=track, album=album, artist=artist)

@tidal_bp.route("/track/<int:id>/download", methods=['POST'])
def downloadTrack(id):
  track = getTidalTrack(id)
  track.downloaded = False
  track.queued = True
  updateTidalTrack(track)

  return "OK"

@tidal_bp.route("/tracks")
def tidalTracks():
    tracks = getTidalTracks()
    return render_template("tidal/tracks.html", tracks = tracks)