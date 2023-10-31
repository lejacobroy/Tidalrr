import subprocess
import sys
from flask import Blueprint, render_template, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from tidalrr.database import *
from tidalrr.tidal import *
main_bp = Blueprint('main', __name__)

# Define a UserSettingsForm
class UserSettingsForm(FlaskForm):
    albumFolderFormat = StringField('albumFolderFormat', validators=[DataRequired()])
    apiKeyIndex = SelectField('apiKeyIndex', choices=[('1', 1), ('2', 2), ('3', 3), ('4', 4)])
    audioQuality = SelectField('audioQuality', choices=[('Normal', 'Normal'), ('High', 'High'), ('Master', 'Master'), ('Max', 'Max')])
    downloadPath = StringField('downloadPath', validators=[DataRequired()])
    includeEP = BooleanField('includeEP')
    lyricFile = BooleanField('lyricFile')
    usePlaylistFolder = BooleanField('usePlaylistFolder')
    playlistFolderFormat = StringField('playlistFolderFormat', validators=[DataRequired()])
    saveAlbumInfo = BooleanField('saveAlbumInfo')
    saveCovers = BooleanField('saveCovers')
    trackFileFormat = StringField('trackFileFormat', validators=[DataRequired()])
    lidarrUrl = StringField('lidarrUrl')
    lidarrApi = StringField('lidarrApi')
    plexUrl = StringField('plexUrl')
    plexToken = StringField('plexToken')
    tidalToken = StringField('tidalToken')
    submit = SubmitField('Save Settings')

def startWaitForAuth():
    url = getDeviceCode()
    key = getTidalKey()
    timeout = displayTime(int(key.authCheckTimeout))
    # start subprocess to waitFroAuth()
    try:
        process = subprocess.Popen([sys.executable, 'runWaitForAuth.py'])
    except subprocess.CalledProcessError as e:
        return f"Script execution failed: {e.output}"
    return url, timeout

@main_bp.route("/")
def hello_world():
    url = ''
    timeout = ''
    settings = getSettings()
    if not isItemValid(settings.apiKeyIndex):
        changeApiKey()
        url, timeout = startWaitForAuth()
        
    elif not loginByConfig():
        url, timeout = startWaitForAuth()

    return render_template("content.html", url=url, timeout=timeout)

@main_bp.route('/settings', methods=['GET', 'POST'])
def settingsPage():
    # Simulate user data, you should replace this with your own user data retrieval logic
    settings = getSettings()

    # Create a form and prepopulate it with the user's current settings
    form = UserSettingsForm(
        albumFolderFormat=settings.albumFolderFormat,
        apiKeyIndex=settings.apiKeyIndex,
        audioQuality=settings.audioQuality,
        downloadPath=settings.downloadPath,
        includeEP=settings.includeEP,
        lyricFile=settings.lyricFile,
        usePlaylistFolder=settings.usePlaylistFolder,
        playlistFolderFormat=settings.playlistFolderFormat,
        trackFileFormat=settings.trackFileFormat,
        saveAlbumInfo=settings.saveAlbumInfo,
        saveCovers=settings.saveCovers,
        lidarrUrl=settings.lidarrUrl,
        lidarrApi=settings.lidarrApi,
        plexUrl=settings.plexUrl,
        plexToken=settings.plexToken,
        tidalToken=settings.tidalToken
        )

    if request.method == 'POST':
        # Handle form submission and update user settings
        if form.validate_on_submit():
            settings.albumFolderFormat = form.albumFolderFormat.data
            settings.apiKeyIndex = form.apiKeyIndex.data
            settings.audioQuality = form.audioQuality.data
            settings.downloadPath = form.downloadPath.data
            settings.includeEP = form.includeEP.data
            settings.lyricFile = form.lyricFile.data
            settings.usePlaylistFolder = form.usePlaylistFolder.data
            settings.playlistFolderFormat = form.playlistFolderFormat.data
            settings.trackFileFormat = form.trackFileFormat.data
            settings.saveAlbumInfo = form.saveAlbumInfo.data
            settings.saveCovers = form.saveCovers.data
            settings.lidarrUrl = form.lidarrUrl.data
            settings.lidarrApi = form.lidarrApi.data
            settings.plexUrl = form.plexUrl.data
            settings.plexToken = form.plexToken.data
            settings.tidalToken = form.tidalToken.data
            setSettings(settings)
            # You should save the updated user settings to your database here

    return render_template('config/settings.html', form=form)

@main_bp.route("/stats")
def stats():
    rows = getStats()
    return render_template("config/stats.html", rows = rows)

@main_bp.route("/download/queue")
def tidalQueues():
    rows = getTidalQueues('')
    return render_template("config/queues.html", rows = rows)
    
@main_bp.route("/files")
def files():
    rows = getFiles()
    return render_template("config/files.html", rows = rows)