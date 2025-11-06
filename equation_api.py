from flask import Blueprint, request, jsonify, send_file
from typing import Dict, List, Any
import os
import tempfile
from werkzeug.utils import secure_filename
from datetime import datetime

# Import core equation service logic
try:
    from equation_core import EquationProcessor
    from equation_excel import EquationExcelProcessor
except ImportError:
    # Fallback when running as a package
    from .equation_core import EquationProcessor  # type: ignore
    from .equation_excel import EquationExcelProcessor  # type: ignore

equation_bp = Blueprint('equation_api', __name__)

# Initialize processors
equation_processor = EquationProcessor()
excel_processor = EquationExcelProcessor()

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@equation_bp.route('/operations', methods=['GET'])
def get_operations():
    try:
        return jsonify({"status": "success","data": ["Hệ phương trình 2 ẩn","Hệ phương trình 3 ẩn","Hệ phương trình 4 ẩn"]})
    except Exception as e:
        return jsonify({"status": "error","message": str(e)}), 500

# Unicode-based template endpoint
@equation_bp.route('/templates/<operation>', methods=['GET'])
def get_template(operation):
    templates = {
        "Hệ phương trình 2 ẩn": {"variables": 2, "equations": [
            {"label": "Phương trình 1 (a₁₁, a₁₂, c₁)", "fields": ["a11", "a12", "c1"]},
            {"label": "Phương trình 2 (a₂₁, a₂₂, c₂)", "fields": ["a21", "a22", "c2"]}
        ], "description": "Nhập hệ số cho hệ phương trình ax + by = c"},
        "Hệ phương trình 3 ẩn": {"variables": 3, "equations": [
            {"label": "Phương trình 1 (a₁₁, a₁₂, a₁₃, c₁)", "fields": ["a11", "a12", "a13", "c1"]},
            {"label": "Phương trình 2 (a₂₁, a₂₂, a₂₃, c₂)", "fields": ["a21", "a22", "a23", "c2"]},
            {"label": "Phương trình 3 (a₃₁, a₃₂, a₃₃, c₃)", "fields": ["a31", "a32", "a33", "c3"]}
        ], "description": "Nhập hệ số cho hệ phương trình ax + by + cz = d"},
        "Hệ phương trình 4 ẩn": {"variables": 4, "equations": [
            {"label": "Phương trình 1 (a₁₁, a₁₂, a₁₃, a₁₄, c₁)", "fields": ["a11", "a12", "a13", "a14", "c1"]},
            {"label": "Phương trình 2 (a₂₁, a₂₂, a₂₃, a₂₄, c₂)", "fields": ["a21", "a22", "a23", "a24", "c2"]},
            {"label": "Phương trình 3 (a₃₁, a₃₂, a₃₃, a₃₄, c₃)", "fields": ["a31", "a32", "a33", "a34", "c3"]},
            {"label": "Phương trình 4 (a₄₁, a₄₂, a₄₃, a₄₄, c₄)", "fields": ["a41", "a42", "a43", "a44", "c4"]}
        ], "description": "Nhập hệ số cho hệ phương trình 4 ẩn"}
    }
    if operation in templates:
        return jsonify({"status": "success", "data": templates[operation]})
    return jsonify({"status": "error", "message": "Operation not found"}), 404

# ASCII alias endpoints to avoid Unicode/encoding issues
@equation_bp.route('/templates/he-2-an', methods=['GET'])
@equation_bp.route('/templates/he-3-an', methods=['GET'])
@equation_bp.route('/templates/he-4-an', methods=['GET'])
def get_template_alias():
    path = request.path.rsplit('/', 1)[-1]
    mapping = {
        'he-2-an': "Hệ phương trình 2 ẩn",
        'he-3-an': "Hệ phương trình 3 ẩn",
        'he-4-an': "Hệ phương trình 4 ẩn"
    }
    op = mapping.get(path)
    return get_template(op) if op else (jsonify({"status":"error","message":"Operation not found"}),404)

@equation_bp.route('/process', methods=['POST'])
def process_equation():
    try:
        data = request.get_json() or {}
        operation = data.get('operation')
        equations = data.get('equations', [])
        version = data.get('version', 'fx799')
        if not operation or not equations:
            return jsonify({"status":"error","message":"Missing required fields: operation, equations"}), 400
        result = equation_processor.process_single(operation, equations, version)
        if result.get('success'):
            return jsonify({"status":"success","data":{
                "operation": operation,
                "keylog": result['keylog'],
                "solutions": result['solutions'],
                "encoded_coefficients": result['encoded_coefficients'],
                "matrix_info": result.get('matrix_info', {}),
                "version": version
            }})
        return jsonify({"status":"error","message": result.get('error','Processing failed')}), 400
    except Exception as e:
        return jsonify({"status":"error","message": str(e)}), 500

@equation_bp.route('/batch', methods=['POST'])
def process_equation_batch():
    try:
        data = request.get_json() or {}
        calculations = data.get('calculations', [])
        if not calculations:
            return jsonify({"status":"error","message":"No calculations provided"}), 400
        results = []
        for calc in calculations:
            results.append(equation_processor.process_single(
                calc.get('operation'), calc.get('equations', []), calc.get('version','fx799')
            ))
        return jsonify({"status":"success","data": results})
    except Exception as e:
        return jsonify({"status":"error","message": str(e)}), 500

# ========== NEW EXCEL ENDPOINTS ==========

@equation_bp.route('/excel/upload', methods=['POST'])
def upload_excel():
    """Upload Excel file for equation processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'status': 'error', 'message': 'Invalid file type. Only .xlsx and .xls files are allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Get file info
        file_info = excel_processor.get_file_info(filepath)
        
        return jsonify({
            'status': 'success',
            'message': 'File uploaded successfully',
            'data': {
                'filename': filename,
                'filepath': filepath,
                'file_info': file_info
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@equation_bp.route('/excel/validate', methods=['POST'])
def validate_excel():
    """Validate Excel file structure for equation processing"""
    try:
        data = request.get_json() or {}
        filepath = data.get('filepath')
        operation = data.get('operation')
        
        if not filepath or not operation:
            return jsonify({'status': 'error', 'message': 'Missing filepath or operation'}), 400
        
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
        # Read and validate Excel file
        df = excel_processor.read_excel_data(filepath)
        is_valid, missing_cols = excel_processor.validate_excel_structure(df, operation)
        
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': 'Invalid Excel structure',
                'missing_columns': missing_cols
            }), 400
        
        # Validate data quality
        quality_info = excel_processor.validate_data_quality(df, operation)
        
        return jsonify({
            'status': 'success',
            'message': 'Excel file validation completed',
            'data': {
                'is_valid': quality_info['valid'],
                'validation_results': quality_info
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@equation_bp.route('/excel/process', methods=['POST'])
def process_excel():
    """Process Excel file with equation data"""
    try:
        data = request.get_json() or {}
        filepath = data.get('filepath')
        operation = data.get('operation')
        version = data.get('version', 'fx799')
        
        if not filepath or not operation:
            return jsonify({'status': 'error', 'message': 'Missing filepath or operation'}), 400
        
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
        # Process Excel file
        processed_count, error_count, output_path = excel_processor.process_excel_equations(
            filepath, operation, version
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Excel processing completed',
            'data': {
                'processed_count': processed_count,
                'error_count': error_count,
                'output_file': os.path.basename(output_path),
                'output_path': output_path
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@equation_bp.route('/excel/download/<filename>', methods=['GET'])
def download_result(filename):
    """Download processed result file"""
    try:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@equation_bp.route('/excel/template/<operation>', methods=['GET'])
def download_template(operation):
    """Download Excel template for equation operation"""
    try:
        # Create template file
        timestamp = int(datetime.now().timestamp())
        template_filename = f"equation_template_{operation.replace(' ', '_')}_{timestamp}.xlsx"
        template_path = os.path.join(UPLOAD_FOLDER, template_filename)
        
        excel_processor.create_equation_template(operation, template_path)
        
        if not os.path.exists(template_path):
            return jsonify({'status': 'error', 'message': 'Failed to create template'}), 500
        
        return send_file(template_path, as_attachment=True, download_name=template_filename)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ASCII template download endpoints
@equation_bp.route('/excel/template/he-2-an', methods=['GET'])
def download_template_2():
    return download_template("Hệ phương trình 2 ẩn")

@equation_bp.route('/excel/template/he-3-an', methods=['GET'])
def download_template_3():
    return download_template("Hệ phương trình 3 ẩn")

@equation_bp.route('/excel/template/he-4-an', methods=['GET'])
def download_template_4():
    return download_template("Hệ phương trình 4 ẩn")