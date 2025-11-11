from flask import Blueprint, request, jsonify
from datetime import datetime
import re
from utils.config_loader import ConfigLoader

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

# Single instance
poly_api = PolynomialAPI()

@polynomial_bp.route('/process', methods=['POST'])
def process_polynomial():
    try:
        data = request.get_json() or {}
        degree = data.get('degree')
        coefficients = data.get('coefficients', [])
        version = data.get('version', 'fx799')
        if not degree or not coefficients:
            return jsonify({'status': 'error', 'message': 'Missing degree or coefficients'}), 400
        keylog = poly_api.generate_keylog(degree, coefficients, version)
        return jsonify({'status': 'success', 'data': {'keylog': keylog, 'degree': degree, 'coefficients': coefficients, 'encoded_coefficients': [poly_api.encode_latex(str(c)) for c in coefficients], 'version': version, 'timestamp': datetime.now().isoformat()}})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
