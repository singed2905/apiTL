from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

# Import blueprints
try:
    from geometry_blueprint import geometry_bp
except Exception as e:
    geometry_bp = None
    print(f"[WARN] geometry_blueprint import failed: {e}")

try:
    from equation_api import equation_bp
except Exception as e:
    equation_bp = None
    print(f"[WARN] equation_api import failed: {e}")

try:
    from polynomial_api import polynomial_bp
except Exception as e:
    polynomial_bp = None
    print(f"[WARN] polynomial_api import failed: {e}")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ========== Register Blueprints ==========
if geometry_bp:
    app.register_blueprint(geometry_bp, url_prefix='/api/geometry')
    print("✅ Geometry Blueprint registered")

if equation_bp:
    app.register_blueprint(equation_bp, url_prefix='/api/equation')
    print("✅ Equation Blueprint registered")

if polynomial_bp:
    app.register_blueprint(polynomial_bp, url_prefix='/api/polynomial')
    print("✅ Polynomial Blueprint registered")

# ========== Static Files Serving ==========
BASE_DIR = os.path.dirname(__file__)
EXAMPLES_DIR = os.path.join(BASE_DIR, 'examples')

@app.route('/examples/<path:filename>')
def serve_examples(filename: str):
    """Serve HTML example files"""
    return send_from_directory(EXAMPLES_DIR, filename)

@app.route('/examples/')
def list_examples():
    """List all available HTML examples"""
    files = []
    try:
        files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith('.html')]
    except Exception:
        pass
    return jsonify({
        'status': 'success',
        'files': files
    })

# ========== Health Check & API Documentation ==========
@app.route('/')
def home():
    """API health check and endpoint documentation"""
    endpoints = {
        'examples': [
            '/examples/',
            '/examples/equation_test.html',
            '/examples/equation_excel_test.html',
            '/examples/geometry_example.html',
            '/examples/polynomial-final.html'
        ],
        'geometry': [
            '/api/geometry/shapes',
            '/api/geometry/operations',
            '/api/geometry/operations/<operation>/shapes',
            '/api/geometry/process',
            '/api/geometry/batch',
            '/api/geometry/validate',
            '/api/geometry/template/<shape_a>',
            '/api/geometry/template/<shape_a>/<shape_b>'
        ] if geometry_bp else [],
        'equation': [
            '/api/equation/operations',
            '/api/equation/templates/<operation>',
            '/api/equation/process',
            '/api/equation/batch',
            '/api/equation/excel/upload',
            '/api/equation/excel/validate',
            '/api/equation/excel/process',
            '/api/equation/excel/download/<filename>',
            '/api/equation/excel/template/<operation>'
        ] if equation_bp else [],
        'polynomial': [
            '/api/polynomial/degrees',
            '/api/polynomial/template/<degree>',
            '/api/polynomial/process',
            '/api/polynomial/solve',
            '/api/polynomial/batch'
        ] if polynomial_bp else []
    }
    
    return jsonify({
        'status': 'success',
        'message': 'ConvertKeylogApp Multi-Mode API',
        'version': '1.5.0',
        'timestamp': datetime.now().isoformat(),
        'available_endpoints': endpoints,
        'changelog': {
            'v1.5.0': [
                'Refactored Geometry API to Blueprint pattern',
                'Added validation endpoint for Geometry',
                'Added template endpoints for Geometry',
                'Consistent API structure across all modes',
                'Improved code organization and maintainability'
            ]
        },
        'documentation': 'https://github.com/singed2905/apiTL'
    })

# ========== Error Handlers ==========

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'available_endpoints': '/'
    }), 404

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'status': 'error',
        'message': 'File too large. Maximum size is 16MB.'
    }), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

# ========== Application Entry Point ==========

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("\n" + "="*60)
    print("🚀 ConvertKeylogApp Multi-Mode API v1.5.0")
    print("="*60)
    print(f"📍 Server: http://localhost:{port}")
    print(f"📋 API Docs: http://localhost:{port}/")
    print(f"🧪 Examples: http://localhost:{port}/examples/")
    print(f"🔧 Debug Mode: {debug}")
    print("="*60)
    print("\n✨ What's New in v1.5.0:")
    print("  • Geometry API refactored to Blueprint pattern")
    print("  • Added /api/geometry/validate endpoint")
    print("  • Added /api/geometry/template endpoints")
    print("  • Cleaner code structure and better maintainability")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
