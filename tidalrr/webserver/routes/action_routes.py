from flask import Blueprint, render_template
from tidalrr.database import *
actions_bp = Blueprint('actions', __name__)

LOG_FOLDER = 'logs'

def view_log(log_filename):
    log_path = os.path.join(LOG_FOLDER, log_filename)
    if os.path.exists(log_path):
        with open(log_path, 'r') as log_file:
            log_content = log_file.read()
        return log_content
    else:
        return 'Log file not found'

@actions_bp.route("/actions/uploadUrlsFile")
def uploadUrlsfile():
    return render_template("actions/uploadUrlsFile.html")

@actions_bp.route("/actions/run-import")
def actionsRunImport():
    log_filename = f"script_log_import.txt"
    log_content = view_log(log_filename)
    return render_template("actions/run-import.html", log_content=log_content)

@actions_bp.route("/actions/run-scans")
def actionsRunScans():
    log_filename = f"script_log_scans.txt"
    log_content = view_log(log_filename)
    return render_template("actions/run-scans.html", log_content=log_content)

@actions_bp.route("/actions/run-downloads")
def actionsRunDownloads():
    log_filename = f"script_log_downloads.txt"
    log_content = view_log(log_filename)
    return render_template("actions/run-downloads.html", log_content=log_content)