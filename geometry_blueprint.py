"""
Geometry API Blueprint
Refactored from app.py to follow Blueprint pattern
Consistent with equation_api and polynomial_api structure
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from geometry_api import GeometryAPI

geometry_bp = Blueprint('geometry', __name__)

# Initialize geometry service
geometry_service = GeometryAPI()

# ========== Metadata Endpoints ==========

@geometry_bp.route('/shapes', methods=['GET'])
def get_shapes():
    """Get list of available geometric shapes"""
    try:
        return jsonify({
            'status': 'success',
            'data': geometry_service.get_available_shapes()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@geometry_bp.route('/operations', methods=['GET'])
def get_operations():
    """Get list of available operations"""
    try:
        return jsonify({
            'status': 'success',
            'data': geometry_service.get_available_operations()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@geometry_bp.route('/operations/<operation>/shapes', methods=['GET'])
def get_shapes_for_operation(operation: str):
    """Get compatible shapes for a specific operation"""
    try:
        return jsonify({
            'status': 'success',
            'operation': operation,
            'data': geometry_service.get_shapes_for_operation(operation)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ========== Processing Endpoints ==========

@geometry_bp.route('/process', methods=['POST', 'OPTIONS'])
def process_geometry():
    """Process single geometry calculation"""
    if request.method == 'OPTIONS':
        return ('', 204)
    
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        required_fields = ['operation', 'shape_A', 'data_A']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Process geometry
        result = geometry_service.process_geometry(
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
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@geometry_bp.route('/batch', methods=['POST'])
def process_batch():
    """Process multiple geometry calculations"""
    try:
        data = request.get_json() or {}
        calculations = data.get('calculations')
        
        if not isinstance(calculations, list):
            return jsonify({
                'status': 'error',
                'message': 'calculations must be an array'
            }), 400
        
        results = []
        errors = []
        
        for i, calc in enumerate(calculations):
            try:
                result = geometry_service.process_geometry(
                    operation=calc['operation'],
                    shape_A=calc['shape_A'],
                    data_A=calc['data_A'],
                    shape_B=calc.get('shape_B'),
                    data_B=calc.get('data_B'),
                    dimension_A=calc.get('dimension_A', '3'),
                    dimension_B=calc.get('dimension_B', '3'),
                    version=calc.get('version', 'fx799')
                )
                results.append(result)
            except Exception as e:
                errors.append({'index': i, 'error': str(e)})
                results.append(None)
        
        return jsonify({
            'status': 'success',
            'total_processed': len(calculations),
            'successful': len([r for r in results if r]),
            'errors': len(errors),
            'data': results,
            'error_details': errors if errors else None
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ========== Validation Endpoints ==========

@geometry_bp.route('/validate', methods=['POST'])
def validate_input():
    """Validate geometry input data"""
    try:
        data = request.get_json() or {}
        validation_result = geometry_service.validate_input_data(data)
        
        if validation_result['valid']:
            return jsonify({
                'status': 'success',
                'message': 'Input data is valid',
                'warnings': validation_result.get('warnings', [])
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Input validation failed',
                'errors': validation_result['errors'],
                'warnings': validation_result.get('warnings', [])
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ========== Template Endpoints ==========

@geometry_bp.route('/template/<shape_a>', methods=['GET'])
def get_template_single(shape_a: str):
    """Get input template for single shape"""
    try:
        shape_info = geometry_service.geometry_shapes.get('shapes', {}).get(shape_a)
        
        if not shape_info:
            return jsonify({
                'status': 'error',
                'message': f'Invalid shape: {shape_a}'
            }), 404
        
        return jsonify({
            'status': 'success',
            'shape': shape_a,
            'template': _get_shape_template(shape_a)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@geometry_bp.route('/template/<shape_a>/<shape_b>', methods=['GET'])
def get_template_pair(shape_a: str, shape_b: str):
    """Get input template for shape pair"""
    try:
        return jsonify({
            'status': 'success',
            'shape_A': shape_a,
            'shape_B': shape_b,
            'template_A': _get_shape_template(shape_a),
            'template_B': _get_shape_template(shape_b)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ========== Helper Functions ==========

def _get_shape_template(shape: str) -> dict:
    """Get input template structure for a shape"""
    templates = {
        'Điểm': {
            'fields': ['point_input'],
            'description': 'Tọa độ dạng phân cách bằng dấu phẩy',
            'example': {'point_input': '1,2,3'},
            'example_2d': {'point_input': '1,2'},
            'notes': 'Cho 2D: x,y | Cho 3D: x,y,z'
        },
        'Đường thẳng': {
            'fields': ['line_A1', 'line_X1'],
            'description': 'Điểm trên đường thẳng và vector chỉ phương',
            'example': {
                'line_A1': '1,2,3',
                'line_X1': '1,0,0'
            },
            'notes': 'line_A1: điểm (x,y,z), line_X1: vector (dx,dy,dz)'
        },
        'Mặt phẳng': {
            'fields': ['plane_a', 'plane_b', 'plane_c', 'plane_d'],
            'description': 'Phương trình mặt phẳng ax + by + cz + d = 0',
            'example': {
                'plane_a': '1',
                'plane_b': '2',
                'plane_c': '3',
                'plane_d': '-6'
            },
            'notes': 'Hệ số có thể là số hoặc biểu thức LaTeX (sqrt, frac, ...)'
        },
        'Đường tròn': {
            'fields': ['circle_center', 'circle_radius'],
            'description': 'Tâm và bán kính đường tròn',
            'example': {
                'circle_center': '0,0',
                'circle_radius': '5'
            },
            'notes': 'circle_center: (x,y), circle_radius: r'
        },
        'Mặt cầu': {
            'fields': ['sphere_center', 'sphere_radius'],
            'description': 'Tâm và bán kính mặt cầu',
            'example': {
                'sphere_center': '0,0,0',
                'sphere_radius': '3'
            },
            'notes': 'sphere_center: (x,y,z), sphere_radius: r'
        }
    }
    
    return templates.get(shape, {
        'error': f'No template found for shape: {shape}'
    })
