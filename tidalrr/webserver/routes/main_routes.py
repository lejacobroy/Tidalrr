from flask import Blueprint, render_template
from tidalrr.database import *
main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def hello_world():
    return render_template("content.html")

@main_bp.route("/config")
def config():
    row = getSettings()
    return render_template("config/settings.html", settings = row)

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