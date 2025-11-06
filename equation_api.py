from flask import Blueprint, request, jsonify
from typing import Dict, List, Any

# Import core equation service logic (use absolute import for script execution)
try:
    from equation_core import EquationProcessor
except ImportError:
    # Fallback when running as a package
    from .equation_core import EquationProcessor  # type: ignore

equation_bp = Blueprint('equation_api', __name__)

# Initialize equation processor
equation_processor = EquationProcessor()

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
