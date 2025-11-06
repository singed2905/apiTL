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
    """Get available equation operations"""
    try:
        operations = [
            "Hệ phương trình 2 ẩn",
            "Hệ phương trình 3 ẩn", 
            "Hệ phương trình 4 ẩn"
        ]
        return jsonify({
            "status": "success",
            "data": operations
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ... rest of file unchanged ...
