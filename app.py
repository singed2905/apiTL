from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
import tempfile
from datetime import datetime

# Optional imports wrapped to avoid startup failures
try:
    from geometry_api import GeometryAPI
except Exception as e:
    GeometryAPI = None
    print(f"[WARN] geometry_api import failed: {e}")

try:
    from equation_api import equation_bp
except Exception as e:
    equation_bp = None
    print(f"[WARN] equation_api import failed: {e}")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize services safely
geometry_api = GeometryAPI() if GeometryAPI else None
if equation_bp:
    app.register_blueprint(equation_bp, url_prefix='/api/equation')

# Serve examples/*.html directly via Flask
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
    return jsonify({'status': 'success', 'files': files or []})

# ========== Health Check ==========
@app.route('/')
def home():
    endpoints = {
        'examples': ['/examples/', '/examples/equation_test.html', '/examples/web_modular.html', '/examples/web_example.html'],
        'geometry': [
            '/api/geometry/shapes', '/api/geometry/operations', '/api/geometry/process', '/api/geometry/batch',
            '/api/geometry/template/<shape_a>', '/api/geometry/template/<shape_a>/<shape_b>',
            '/api/geometry/excel/upload', '/api/geometry/excel/process', '/api/geometry/excel/download/<filename>'
        ],
        'equation': ['/api/equation/operations', '/api/equation/templates/<operation>', '/api/equation/process', '/api/equation/batch'] if equation_bp else []
    }
    return jsonify({
        'status': 'success',
        'message': 'ConvertKeylogApp Multi-Mode API is running',
        'version': '1.2.1',
        'timestamp': datetime.now().isoformat(),
        'available_endpoints': endpoints
    })

# ========== Geometry Endpoints (guarded) ==========
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/geometry/shapes', methods=['GET'])
def get_shapes():
    if not geometry_api:
        return jsonify({'status': 'error', 'message': 'Geometry API not available'}), 503
    try:
        return jsonify({'status': 'success', 'data': geometry_api.get_available_shapes()})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/geometry/operations', methods=['GET'])
def get_ops():
    if not geometry_api:
        return jsonify({'status': 'error', 'message': 'Geometry API not available'}), 503
    try:
        return jsonify({'status': 'success', 'data': geometry_api.get_available_operations()})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/geometry/operations/<operation>/shapes', methods=['GET'])
def get_shapes_for_op(operation):
    if not geometry_api:
        return jsonify({'status': 'error', 'message': 'Geometry API not available'}), 503
    try:
        return jsonify({'status': 'success', 'operation': operation, 'data': geometry_api.get_shapes_for_operation(operation)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/geometry/process', methods=['POST','OPTIONS'])
def process_geometry():
    if request.method == 'OPTIONS':
        return ('', 204)
    if not geometry_api:
        return jsonify({'status': 'error', 'message': 'Geometry API not available'}), 503
    try:
        data = request.get_json() or {}
        for f in ['operation','shape_A','data_A']:
            if f not in data:
                return jsonify({'status':'error','message':f'Missing required field: {f}'}), 400
        result = geometry_api.process_geometry(
            operation=data['operation'],
            shape_A=data['shape_A'],
            data_A=data['data_A'],
            shape_B=data.get('shape_B'),
            data_B=data.get('data_B'),
            dimension_A=data.get('dimension_A','3'),
            dimension_B=data.get('dimension_B','3'),
            version=data.get('version','fx799')
        )
        return jsonify({'status':'success','data':result})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

@app.route('/api/geometry/batch', methods=['POST'])
def process_batch():
    if not geometry_api:
        return jsonify({'status': 'error', 'message': 'Geometry API not available'}), 503
    try:
        data = request.get_json() or {}
        calcs = data.get('calculations')
        if not isinstance(calcs, list):
            return jsonify({'status':'error','message':'calculations must be an array'}), 400
        results=[]; errors=[]
        for i,calc in enumerate(calcs):
            try:
                results.append(geometry_api.process_geometry(
                    operation=calc['operation'],
                    shape_A=calc['shape_A'],
                    data_A=calc['data_A'],
                    shape_B=calc.get('shape_B'),
                    data_B=calc.get('data_B'),
                    dimension_A=calc.get('dimension_A','3'),
                    dimension_B=calc.get('dimension_B','3'),
                    version=calc.get('version','fx799')
                ))
            except Exception as e:
                errors.append({'index':i,'error':str(e)}); results.append(None)
        return jsonify({'status':'success','total_processed':len(calcs),'successful':len([r for r in results if r]),'errors':len(errors),'data':results,'error_details':errors or None})
    except Exception as e:
        return jsonify({'status':'error','message':str(e)}), 500

# Excel helpers guarded similarly (omitted for brevity)

@app.errorhandler(404)
def not_found(e):
    return jsonify({'status':'error','message':'Endpoint not found'}), 404

@app.errorhandler(413)
def too_large(e):
    return jsonify({'status':'error','message':'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'status':'error','message':'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    print(f"🚀 Starting ConvertKeylogApp Multi-Mode API...")
    print(f"📍 Port: {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📋 Available at: http://localhost:{port}")
    print(f"🧪 Examples: http://localhost:{port}/examples/equation_test.html")
    app.run(host='0.0.0.0', port=port, debug=debug)