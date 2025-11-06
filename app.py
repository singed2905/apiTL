from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from geometry_api import GeometryAPI
from equation_api import equation_bp
from werkzeug.utils import secure_filename
import os
import pandas as pd
import tempfile
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for web integration

# Initialize Geometry API
geometry_api = GeometryAPI()

# Register equation API blueprint
app.register_blueprint(equation_bp, url_prefix='/api/equation')

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# -------- Serve example HTML directly via Flask (no separate server needed) --------
BASE_DIR = os.path.dirname(__file__)
EXAMPLES_DIR = os.path.join(BASE_DIR, 'examples')

@app.route('/examples/<path:filename>')
def serve_examples(filename: str):
    return send_from_directory(EXAMPLES_DIR, filename)

@app.route('/examples/')
def list_examples():
    files = []
    try:
        files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith('.html')]
    except Exception:
        pass
    return jsonify({
        'status': 'success',
        'files': files or ['web_modular.html', 'web_example.html', 'equation_test.html']
    })


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ... rest of file stays the same below ...
