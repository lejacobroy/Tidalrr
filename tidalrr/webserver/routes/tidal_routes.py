from flask import Blueprint, render_template
from tidalrr.database import *
tidal_bp = Blueprint('tidal', __name__)

@tidal_bp.route("/artists")
def tidalArtists():
    rows = getTidalArtists()
    return render_template("tidal/artists.html", rows = rows)

@tidal_bp.route("/albums")
def tidalAlbums():
    rows = getTidalAlbums()
    return render_template("tidal/albums.html", rows = rows)

@tidal_bp.route("/playlists")
def tidalPlaylists():
    rows = getTidalPlaylists()
    return render_template("tidal/playlists.html", rows = rows)

@tidal_bp.route("/tracks")
def tidalTracks():
    rows = getTidalTracks()
    return render_template("tidal/tracks.html", rows = rows)