#!/usr/bin/env python3
import os

from flask import Flask, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_bootstrap import Bootstrap5
import sqlite3
from database.database import getSettings

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
    def get_db_connection():
        conn = sqlite3.connect('database/database.db')
        conn.row_factory = sqlite3.Row
        return conn

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
        # to read settings we need a KV
        settings = getSettings()
        return render_template("config.html", settings = settings)

    """     @app.route("/foo/<someId>")
            def foo_url_arg(someId):
            return jsonify({"echo": someId}) """

    return app
