from flask import Flask, request, jsonify
from flask_cors import CORS
from geometry_api import GeometryAPI
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for web integration

# Initialize Geometry API
geometry_api = GeometryAPI()

@app.route('/')
def home():
    """API health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'ConvertKeylogApp Geometry API is running',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'available_endpoints': [
            '/api/geometry/shapes',
            '/api/geometry/operations', 
            '/api/geometry/process',
            '/api/geometry/batch',
            '/api/geometry/template'
        ]
    })

@app.route('/api/geometry/shapes', methods=['GET'])
def get_available_shapes():
    """Get list of available geometric shapes"""
    try:
        shapes = geometry_api.get_available_shapes()
        return jsonify({
            'status': 'success',
            'data': shapes
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/geometry/operations', methods=['GET'])
def get_available_operations():
    """Get list of available operations"""
    try:
        operations = geometry_api.get_available_operations()
        return jsonify({
            'status': 'success',
            'data': operations
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/geometry/operations/<operation>/shapes', methods=['GET'])
def get_shapes_for_operation(operation):
    """Get available shapes for a specific operation"""
    try:
        shapes = geometry_api.get_shapes_for_operation(operation)
        return jsonify({
            'status': 'success',
            'operation': operation,
            'data': shapes
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/geometry/process', methods=['POST'])
def process_geometry():
    """Process geometric calculation and generate keylog"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['operation', 'shape_A', 'data_A']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Process the geometry calculation
        result = geometry_api.process_geometry(
            operation=data['operation'],
            shape_A=data['shape_A'],
            data_A=data['data_A'],
            shape_B=data.get('shape_B'),
            data_B=data.get('data_B'),
            dimension_A=data.get('dimension_A', '3'),
            dimension_B=data.get('dimension_B', '3'),
            version=data.get('version', 'fx799')
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': f'Validation error: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error', 
            'message': f'Processing error: {str(e)}'
        }), 500

@app.route('/api/geometry/batch', methods=['POST'])
def process_batch():
    """Process multiple geometric calculations"""
    try:
        data = request.get_json()
        
        # Validate batch data
        if 'calculations' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing calculations array'
            }), 400
            
        if not isinstance(data['calculations'], list):
            return jsonify({
                'status': 'error',
                'message': 'calculations must be an array'
            }), 400
        
        results = geometry_api.process_batch(data['calculations'])
        
        return jsonify({
            'status': 'success',
            'total_processed': len(results),
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Batch processing error: {str(e)}'
        }), 500

@app.route('/api/geometry/template/<shape_a>', methods=['GET'])
def get_template_single(shape_a):
    """Get template structure for single shape"""
    try:
        template = geometry_api.get_input_template(shape_a)
        return jsonify({
            'status': 'success',
            'shape': shape_a,
            'template': template
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/geometry/template/<shape_a>/<shape_b>', methods=['GET'])
def get_template_dual(shape_a, shape_b):
    """Get template structure for dual shapes"""
    try:
        template = geometry_api.get_input_template(shape_a, shape_b)
        return jsonify({
            'status': 'success',
            'shape_A': shape_a,
            'shape_B': shape_b,
            'template': template
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/geometry/validate', methods=['POST'])
def validate_input():
    """Validate geometry input data"""
    try:
        data = request.get_json()
        validation_result = geometry_api.validate_input_data(data)
        
        return jsonify({
            'status': 'success',
            'validation': validation_result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'GET /api/geometry/shapes',
            'GET /api/geometry/operations',
            'GET /api/geometry/operations/<operation>/shapes',
            'POST /api/geometry/process',
            'POST /api/geometry/batch',
            'GET /api/geometry/template/<shape_a>',
            'GET /api/geometry/template/<shape_a>/<shape_b>',
            'POST /api/geometry/validate'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Starting ConvertKeylogApp Geometry API...")
    print(f"📍 Port: {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📋 Available at: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)