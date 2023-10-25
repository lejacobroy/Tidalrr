#!/usr/bin/env python3
import os

from flask import Flask, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_bootstrap import Bootstrap5
from tidalrr.database import *
from tidalrr.workers import *

def tidalrrWeb(config=None):
    app = Flask(__name__)
    bootstrap = Bootstrap5(app)
    # See http://flask.pocoo.org/docs/latest/config/
    app.config.update(dict(DEBUG=True))
    app.config.update(config or {})

    # Setup cors headers to allow all domains
    # https://flask-cors.readthedocs.io/en/latest/
    CORS(app)

    # Definition of the routes. Put them into their own file. See also
    # Flask Blueprints: http://flask.pocoo.org/docs/latest/blueprints
    """ 
        Usefull routes:
        homepage
            - settings/config
            - tidal login
            - list tidal playlists, artists, albums, tracks, mixes
                - downlaod all
                - downlaod selected
                - filter by state (online|downloaded|plex)
                - sync to plex
            - interactive search
            - sync lidarr
                - interactive match with search
            - inject spark
            - maintenance
                - albums with master or max available to upgrade
                - incomplete albums
                - missing covers
                - missing lyrics

    """
    @app.route("/")
    def hello_world():
        return render_template("content.html")
    
    @app.route("/config")
    def config():
        settings = getSettings()
        return render_template("config.html", settings = settings)
    
    @app.route("/tidal/artists")
    def tidalArtists():
        rows = getTidalArtists()
        return render_template("artists.html", rows = rows)
    
    @app.route("/tidal/albums")
    def tidalAlbums():
        rows = getTidalAlbums()
        return render_template("albums.html", rows = rows)
    
    @app.route("/tidal/playlists")
    def tidalPlaylists():
        rows = getTidalPlaylists()
        return render_template("playlists.html", rows = rows)
    
    @app.route("/tidal/tracks")
    def tidalTracks():
        rows = getTidalTracks()
        return render_template("tracks.html", rows = rows)
    
    @app.route("/download/queue")
    def tidalQueues():
        rows = getTidalQueues('')
        return render_template("queues.html", rows = rows)
    
    @app.route("/files")
    def files():
        rows = getFiles()
        return render_template("files.html", rows = rows)

    """     @app.route("/foo/<someId>")
            def foo_url_arg(someId):
            return jsonify({"echo": someId}) """

    return app

def webServer():
    createTables()
    tidalrrStart()
    port = int(os.environ.get("PORT", 3000))
    app = tidalrrWeb()
    app.run(host="0.0.0.0", port=port)