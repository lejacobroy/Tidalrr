from flask import Blueprint, render_template
from tidalrr.database import *
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

@tidal_bp.route("/artist/<int:id>/queue", methods=['POST'])  
def queueArtist(id):
    artist = getTidalArtist(id)
    artist.queued = True
    updateTidalArtist(artist)
    return "OK"

@tidal_bp.route("/artist/<int:id>/unqueue", methods=['POST'])  
def unqueueArtist(id):
    artist = getTidalArtist(id)
    artist.queued = False
    updateTidalArtist(artist)
    return "OK"

@tidal_bp.route("/artist/<int:id>/download", methods=['POST'])
def downloadArtist(id):
    artist = getTidalArtist(id)
    artist.downloaded = False 
    artist.queued = True
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

@tidal_bp.route("/album/<int:id>/queue", methods=['POST'])
def queueAlbum(id):
  album = getTidalAlbum(id)
  album.queued = True
  updateTidalAlbum(album)
  
  return "OK"

@tidal_bp.route("/album/<int:id>/unqueue", methods=['POST'])
def unqueueAlbum(id):
  album = getTidalAlbum(id)
  album.queued = False
  updateTidalAlbum(album)

  delTidalQueue(album.id)

  return "OK"
  
@tidal_bp.route("/album/<int:id>/download", methods=['POST'])  
def downloadAlbum(id):
  album = getTidalAlbum(id)
  album.downloaded = False
  album.queued = True
  updateTidalAlbum(album)

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

@tidal_bp.route("/playlist/<uuid>/queue", methods=['POST'])
def queuePlaylist(uuid):
  playlist = getTidalPlaylist(uuid)
  playlist.queued = True
  updateTidalPlaylist(playlist)

  return "OK"
  
@tidal_bp.route("/playlist/<uuid>/unqueue", methods=['POST'])
def unqueuePlaylist(uuid):
  playlist = getTidalPlaylist(uuid)
  playlist.queued = False
  updateTidalPlaylist(playlist)

  return "OK"

@tidal_bp.route("/playlist/<uuid>/download", methods=['POST'])
def downloadPlaylist(uuid):
  playlist = getTidalPlaylist(uuid)
  playlist.downloaded = False
  playlist.queued = True
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

@tidal_bp.route("/track/<int:id>/queue", methods=['POST']) 
def queueTrack(id):
  track = getTidalTrack(id)
  track.queued = True
  updateTidalTrack(track)

  delTidalQueue(track.id)

  return "OK"

@tidal_bp.route("/track/<int:id>/unqueue", methods=['POST'])
def unqueueTrack(id):
  track = getTidalTrack(id)
  track.queued = False
  updateTidalTrack(track)

  return "OK"  

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