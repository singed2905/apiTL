from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from geometry_api import GeometryAPI
from werkzeug.utils import secure_filename
import os
import pandas as pd
import tempfile
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for web integration

# Initialize Geometry API
geometry_api = GeometryAPI()

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_shape_data_from_row(row, shape, group):
    """Extract shape data from Excel row"""
    if not shape:
        return {}
    
    data = {}
    
    if shape == 'Điểm':
        # Look for point_input or separate x,y,z columns
        point_col = f'point_input_{group}' if f'point_input_{group}' in row else 'point_input'
        if point_col in row and pd.notna(row[point_col]):
            data['point_input'] = str(row[point_col])
        else:
            # Try separate columns
            coords = []
            for coord in ['x', 'y', 'z']:
                col_name = f'{coord}_{group}' if f'{coord}_{group}' in row else coord
                if col_name in row and pd.notna(row[col_name]):
                    coords.append(str(row[col_name]))
            if coords:
                data['point_input'] = ','.join(coords)
    
    elif shape == 'Đường thẳng':
        line_a_col = f'line_A{1 if group == "A" else 2}_{group}' if f'line_A{1 if group == "A" else 2}_{group}' in row else f'line_A{1 if group == "A" else 2}'
        line_x_col = f'line_X{1 if group == "A" else 2}_{group}' if f'line_X{1 if group == "A" else 2}_{group}' in row else f'line_X{1 if group == "A" else 2}'
        
        if line_a_col in row and pd.notna(row[line_a_col]):
            data[f'line_A{1 if group == "A" else 2}'] = str(row[line_a_col])
        if line_x_col in row and pd.notna(row[line_x_col]):
            data[f'line_X{1 if group == "A" else 2}'] = str(row[line_x_col])
    
    elif shape == 'Mặt phẳng':
        for coeff in ['a', 'b', 'c', 'd']:
            col_name = f'plane_{coeff}_{group}' if f'plane_{coeff}_{group}' in row else f'plane_{coeff}'
            if col_name in row and pd.notna(row[col_name]):
                data[f'plane_{coeff}'] = str(row[col_name])
    
    elif shape == 'Đường tròn':
        center_col = f'circle_center_{group}' if f'circle_center_{group}' in row else 'circle_center'
        radius_col = f'circle_radius_{group}' if f'circle_radius_{group}' in row else 'circle_radius'
        
        if center_col in row and pd.notna(row[center_col]):
            data['circle_center'] = str(row[center_col])
        if radius_col in row and pd.notna(row[radius_col]):
            data['circle_radius'] = str(row[radius_col])
    
    elif shape == 'Mặt cầu':
        center_col = f'sphere_center_{group}' if f'sphere_center_{group}' in row else 'sphere_center'
        radius_col = f'sphere_radius_{group}' if f'sphere_radius_{group}' in row else 'sphere_radius'
        
        if center_col in row and pd.notna(row[center_col]):
            data['sphere_center'] = str(row[center_col])
        if radius_col in row and pd.notna(row[radius_col]):
            data['sphere_radius'] = str(row[radius_col])
    
    return data

@app.route('/')
def home():
    """API health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'ConvertKeylogApp Geometry API is running',
        'version': '1.1.0',
        'timestamp': datetime.now().isoformat(),
        'available_endpoints': [
            '/api/geometry/shapes',
            '/api/geometry/operations', 
            '/api/geometry/process',
            '/api/geometry/batch',
            '/api/geometry/template',
            '/api/geometry/excel/upload',
            '/api/geometry/excel/process',
            '/api/geometry/excel/download'
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
        
        results = []
        errors = []
        
        for i, calc in enumerate(data['calculations']):
            try:
                result = geometry_api.process_geometry(
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
                error_info = {
                    'index': i,
                    'error': str(e),
                    'calculation': calc
                }
                errors.append(error_info)
                results.append(None)
        
        return jsonify({
            'status': 'success',
            'total_processed': len(data['calculations']),
            'successful': len([r for r in results if r is not None]),
            'errors': len(errors),
            'data': results,
            'error_details': errors if errors else None
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Batch processing error: {str(e)}'
        }), 500

# Excel Processing Endpoints
@app.route('/api/geometry/excel/upload', methods=['POST'])
def upload_excel():
    """Upload and validate Excel file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': 'Only Excel files (.xlsx, .xls) are allowed'
            }), 400
        
        # Save file to temp directory
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # Validate and preview file
        try:
            # Read first few rows for preview
            df_preview = pd.read_excel(filepath, nrows=5)
            
            # Get total row count
            df_full = pd.read_excel(filepath)
            total_rows = len(df_full)
            
            # Get file size
            file_size = os.path.getsize(filepath)
            file_size_mb = round(file_size / (1024 * 1024), 2)
            
            return jsonify({
                'status': 'success',
                'filepath': unique_filename,  # Only return filename for security
                'filename': filename,
                'columns': list(df_preview.columns),
                'preview': df_preview.to_dict('records'),
                'total_rows': total_rows,
                'file_size_mb': file_size_mb,
                'upload_time': datetime.now().isoformat()
            })
            
        except Exception as e:
            # Clean up file on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({
                'status': 'error',
                'message': f'Failed to read Excel file: {str(e)}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Upload failed: {str(e)}'
        }), 500

@app.route('/api/geometry/excel/process', methods=['POST'])
def process_excel_batch():
    """Process Excel file batch"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['filepath', 'operation', 'shape_A']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        filepath = os.path.join(UPLOAD_FOLDER, data['filepath'])
        
        if not os.path.exists(filepath):
            return jsonify({
                'status': 'error',
                'message': 'Uploaded file not found or expired'
            }), 404
        
        operation = data['operation']
        shape_A = data['shape_A']
        shape_B = data.get('shape_B')
        version = data.get('version', 'fx799')
        
        # Read Excel file
        df = pd.read_excel(filepath)
        
        results = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Extract data from row
                data_A = extract_shape_data_from_row(row, shape_A, 'A')
                data_B = extract_shape_data_from_row(row, shape_B, 'B') if shape_B else None
                
                # Process geometry
                result = geometry_api.process_geometry(
                    operation=operation,
                    shape_A=shape_A,
                    data_A=data_A,
                    shape_B=shape_B,
                    data_B=data_B,
                    dimension_A='3',  # Default to 3D
                    dimension_B='3',
                    version=version
                )
                
                results.append(result['keylog'])
                
            except Exception as e:
                error_msg = f"Row {index + 1}: {str(e)}"
                errors.append(error_msg)
                results.append(f"ERROR: {str(e)}")
        
        # Add keylog column to DataFrame
        df['keylog'] = results
        
        # Generate output filename
        original_name = os.path.splitext(data['filepath'])[0]
        output_filename = f"{original_name}_result.xlsx"
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        # Save result file
        df.to_excel(output_path, index=False)
        
        # Clean up original file
        try:
            os.remove(filepath)
        except:
            pass  # Ignore cleanup errors
        
        return jsonify({
            'status': 'success',
            'processed_rows': len(results),
            'successful_rows': len([r for r in results if not r.startswith('ERROR')]),
            'error_count': len(errors),
            'output_file': output_filename,
            'errors': errors if errors else None,
            'processing_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Excel processing failed: {str(e)}'
        }), 500

@app.route('/api/geometry/excel/download/<filename>', methods=['GET'])
def download_result(filename):
    """Download processed Excel result file"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        
        if not os.path.exists(filepath):
            return jsonify({
                'status': 'error',
                'message': 'File not found or expired'
            }), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Download failed: {str(e)}'
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
            'POST /api/geometry/excel/upload',
            'POST /api/geometry/excel/process',
            'GET /api/geometry/excel/download/<filename>',
            'GET /api/geometry/template/<shape_a>',
            'GET /api/geometry/template/<shape_a>/<shape_b>',
            'POST /api/geometry/validate'
        ]
    }), 404

@app.errorhandler(413)
def too_large(error):
    return jsonify({
        'status': 'error',
        'message': 'File too large. Maximum size is 16MB.'
    }), 413

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
    print(f"📊 Excel processing enabled with {UPLOAD_FOLDER}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)