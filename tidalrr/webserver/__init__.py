#!/usr/bin/env python3
import os
import subprocess
import sys

from flask import Flask, jsonify, render_template, redirect, url_for, request, flash
from flask_cors import CORS
from flask_bootstrap import Bootstrap5
from tidalrr.database import *
from tidalrr.workers import *
from routes.main_routes import main_bp
from routes.tidal_routes import tidal_bp
from routes.action_routes import actions_bp

def tidalrrWeb(config=None):
    app = Flask(__name__)
    # Specify the directory where uploaded files will be stored
    UPLOAD_FOLDER = 'import'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Ensure the upload directory exists
    LOG_FOLDER = 'logs'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(LOG_FOLDER, exist_ok=True)
    ALLOWED_EXTENSIONS = {'txt'}
    app.secret_key = 'tidalrr_secret_key'  # Set a secret key for flashing messages

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    bootstrap = Bootstrap5(app)
    # See http://flask.pocoo.org/docs/latest/config/
    app.config.update(dict(DEBUG=True))
    app.config.update(config or {})

    # Setup cors headers to allow all domains
    # https://flask-cors.readthedocs.io/en/latest/
    CORS(app)

    # Register the blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(tidal_bp, url_prefix='/tidal')  # Prefix for upload routes
    app.register_blueprint(actions_bp, url_prefix='/actions')  # Prefix for script-related routes

    """     @app.route("/foo/<someId>")
            def foo_url_arg(someId):
            return jsonify({"echo": someId}) """
        
    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Save the uploaded file to the specified directory
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'urls.txt'))
            flash('File uploaded successfully')
            return redirect('/')

        flash('Invalid file format. Only .txt files are allowed.')
        return redirect(request.url)
    
    @app.route('/run-import')
    def run_import():
        try:
            # Replace 'your_script.py' with the name of the script you want to run
            log_filename = f"script_log_import.txt"
            log_path = os.path.join(LOG_FOLDER, log_filename)

            # Use Popen to run the script and redirect its output to the log file
            with open(log_path, 'w') as log_file:
                process = subprocess.Popen([sys.executable, 'runImportURLs.py'], stdout=log_file, stderr=log_file)
            return redirect('/actions/run-import')
        except subprocess.CalledProcessError as e:
            return f"Script execution failed: {e.output}"
        
    @app.route('/run-scans')
    def run_scans():
        try:
            # Replace 'your_script.py' with the name of the script you want to run
            log_filename = f"script_log_scans.txt"
            log_path = os.path.join(LOG_FOLDER, log_filename)

            # Use Popen to run the script and redirect its output to the log file
            with open(log_path, 'w') as log_file:
                process = subprocess.Popen([sys.executable, 'runScansNow.py'], stdout=log_file, stderr=log_file)
            return redirect('/actions/run-scans')
        except subprocess.CalledProcessError as e:
            return f"Script execution failed: {e.output}"
        
    @app.route('/run-downloads')
    def run_downloads():
        try:
            # Replace 'your_script.py' with the name of the script you want to run
            log_filename = f"script_log_downloads.txt"
            log_path = os.path.join(LOG_FOLDER, log_filename)

            # Use Popen to run the script and redirect its output to the log file
            with open(log_path, 'w') as log_file:
                process = subprocess.Popen([sys.executable, 'runDownloadsNow.py'], stdout=log_file, stderr=log_file)
            return redirect('/actions/run-downloads')
        except subprocess.CalledProcessError as e:
            return f"Script execution failed: {e.output}"
        
    return app

def webServer():
    createTables()
    tidalrrStart()
    print("Starting web server")
    port = int(os.environ.get("PORT", 3000))
    app = tidalrrWeb()
    app.run(host="0.0.0.0", port=port)