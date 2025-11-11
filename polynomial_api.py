from flask import Blueprint, request, jsonify
from datetime import datetime
import re
from utils.config_loader import ConfigLoader
import numpy as np

polynomial_bp = Blueprint('polynomial', __name__)

class PolynomialAPI:
    def __init__(self):
        self.config_loader = ConfigLoader()
        self.equations_config = self.config_loader.load_json('config/polynomial/equations.json')
        self.prefixes_config = self.config_loader.load_json('config/polynomial/prefixes.json')
        self.mappings_config = self.config_loader.load_json('config/polynomial/mappings.json')

    def encode_latex(self, latex_str: str) -> str:
        text = latex_str.replace(' ', '') if latex_str else ''
        for rule in self.mappings_config.get('latex_to_calculator_mappings', []):
            find = rule.get('find', '')
            replace = rule.get('replace', '')
            rtype = rule.get('type', 'literal')
            try:
                if rtype == 'regex':
                    text = re.sub(find, replace, text)
                else:
                    text = text.replace(find, replace)
            except Exception:
                continue
        return text

    def generate_keylog(self, degree: str, coefficients: list, version: str = 'fx799') -> str:
        eq_info = self.equations_config['equations'].get(degree)
        if not eq_info:
            raise ValueError(f"Unsupported degree: {degree}")
        prefix = self.prefixes_config['prefixes'].get(version, {}).get(degree, 'w52')
        suffix = self.prefixes_config.get('suffix', '=')
        encoded_coeffs = [self.encode_latex(str(c)) for c in coefficients]
        return prefix + '='.join(encoded_coeffs) + suffix

    def solve_polynomial(self, degree: str, coefficients: list) -> dict:
        try:
            coeffs = [float(c) for c in coefficients]
            coeffs = list(reversed(coeffs))  # Highest degree first for numpy
            roots = np.roots(coeffs)
            formatted_roots = []
            for root in roots:
                if np.isreal(root):
                    formatted_roots.append({
                        'type': 'real',
                        'value': float(np.real(root)),
                        'display': f"{float(np.real(root)):.6f}"
                    })
                else:
                    formatted_roots.append({
                        'type': 'complex',
                        'real': float(np.real(root)),
                        'imag': float(np.imag(root)),
                        'display': f"{float(np.real(root)):.6f} + {float(np.imag(root)):.6f}i"
                    })
            return {
                'roots': formatted_roots,
                'num_roots': len(formatted_roots)
            }
        except Exception as e:
            return {'error': str(e)}

poly_api = PolynomialAPI()

@polynomial_bp.route('/degrees', methods=['GET'])
def get_degrees():
    try:
        degrees = list(poly_api.equations_config['equations'].keys())
        return jsonify({'status': 'success', 'data': degrees})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@polynomial_bp.route('/template/<degree>', methods=['GET'])
def get_template(degree: str):
    try:
        eq_info = poly_api.equations_config['equations'].get(degree)
        if not eq_info:
            return jsonify({'status': 'error', 'message': f'Invalid degree: {degree}'}), 400
        return jsonify({
            'status': 'success',
            'data': {
                'degree': degree,
                'form': eq_info['form'],
                'coefficients': eq_info['coefficients'],
                'required_fields': eq_info['required_fields']
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@polynomial_bp.route('/process', methods=['POST'])
def process_polynomial():
    try:
        data = request.get_json() or {}
        degree = data.get('degree')
        coefficients = data.get('coefficients', [])
        version = data.get('version', 'fx799')
        solve = data.get('solve', False)
        if not degree or not coefficients:
            return jsonify({'status': 'error', 'message': 'Missing degree or coefficients'}), 400
        keylog = poly_api.generate_keylog(degree, coefficients, version)
        result = {
            'keylog': keylog,
            'degree': degree,
            'coefficients': coefficients,
            'encoded_coefficients': [poly_api.encode_latex(str(c)) for c in coefficients],
            'version': version,
            'timestamp': datetime.now().isoformat()
        }
        if solve:
            result['solution'] = poly_api.solve_polynomial(degree, coefficients)
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@polynomial_bp.route('/solve', methods=['POST'])
def solve_only():
    try:
        data = request.get_json() or {}
        degree = data.get('degree')
        coefficients = data.get('coefficients', [])
        if not degree or not coefficients:
            return jsonify({'status': 'error', 'message': 'Missing degree or coefficients'}), 400
        solution = poly_api.solve_polynomial(degree, coefficients)
        return jsonify({'status': 'success', 'data': {'degree': degree, 'coefficients': coefficients, 'solution': solution, 'timestamp': datetime.now().isoformat()}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@polynomial_bp.route('/batch', methods=['POST'])
def batch_process():
    try:
        data = request.get_json() or {}
        equations = data.get('equations', [])
        if not isinstance(equations, list):
            return jsonify({'status': 'error', 'message': 'equations must be an array'}), 400
        results = []
        errors = []
        for i, eq in enumerate(equations):
            try:
                degree = eq.get('degree')
                coefficients = eq.get('coefficients', [])
                version = eq.get('version', 'fx799')
                solve = eq.get('solve', False)
                keylog = poly_api.generate_keylog(degree, coefficients, version)
                result = {
                    'degree': degree,
                    'coefficients': coefficients,
                    'keylog': keylog,
                    'version': version
                }
                if solve:
                    result['solution'] = poly_api.solve_polynomial(degree, coefficients)
                results.append(result)
            except Exception as e:
                errors.append({'index': i, 'error': str(e)})
                results.append(None)
        return jsonify({'status': 'success', 'total_processed': len(equations), 'successful': len([r for r in results if r]), 'errors': len(errors), 'data': results, 'error_details': errors if errors else None})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
