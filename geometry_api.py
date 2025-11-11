from typing import Dict, Any, List, Union, Optional
from datetime import datetime
import re

from utils.config_loader import ConfigLoader

class GeometryAPI:
    """API wrapper for geometry functionality (config-driven)"""
    
    def __init__(self):
        # Load configs
        self.config_loader = ConfigLoader()
        self.main_config = self.config_loader.get_main()
        
        # Load geometry configuration pieces
        self.geometry_mappings = self.config_loader.get_geometry_mappings().get('mappings', [])
        self.geometry_ops = self.config_loader.get_geometry_operations()
        self.geometry_shapes = self.config_loader.get_geometry_shapes()
        self.encoding_opts = self.config_loader.get_encoding_options()
        
        # Runtime state
        self.current_operation = ""
        self.current_shape_A = ""
        self.current_shape_B = ""
        self.dimension_A = "3"
        self.dimension_B = "3"
        self.current_version = self.main_config.get('default_version', 'fx799')
        
        self.results_A: List[str] = []
        self.results_B: List[str] = []

    # ===== Public metadata =====
    def get_available_shapes(self) -> List[str]:
        return list(self.geometry_shapes.get('shapes', {}).keys())

    def get_available_operations(self) -> List[str]:
        return list(self.geometry_ops.get('operations', {}).keys())

    def get_shapes_for_operation(self, operation: str) -> List[str]:
        filters = self.geometry_shapes.get('operation_filters', {})
        if operation in filters:
            return filters[operation]
        return self.get_available_shapes()

    # ===== Encoding =====
    def encode_string(self, input_string: str) -> str:
        """
        Encode input string using config-driven mapping rules
        Supports both regex and literal replacements
        """
        if not input_string:
            return ""

        # Convert to string and trim spaces
        text = str(input_string)
        if self.encoding_opts.get('trim_spaces', True):
            text = text.replace(' ', '')

        # Priority 1: Handle sqrt(...) with parentheses first
        if self.encoding_opts.get('support_sqrt_paren', True):
            try:
                # Match \sqrt(x) or sqrt(x) and convert to sx)
                text = re.sub(r"\\?sqrt\(([^()]+)\)", r"s\1)", text)
            except Exception as e:
                print(f"[WARN] sqrt pattern failed: {e}")

        # Priority 2: Apply all mapping rules in order
        for idx, rule in enumerate(self.geometry_mappings):
            find = rule.get('find', '')
            replace = rule.get('replace', '')
            rtype = rule.get('type', 'literal')

            if not find:
                continue

            try:
                original = text

                if rtype == 'regex':
                    text = re.sub(find, replace, text)
                elif rtype == 'literal':
                    text = text.replace(find, replace)
                else:
                    print(f"[WARN] Unknown mapping type at index {idx}: {rtype}")

                # Debug logging (optional - comment out in production)
                if text != original:
                    desc = rule.get('description', 'no description')
                    print(f"[DEBUG] Applied rule {idx}: {desc}")
                    print(f"  Before: {original}")
                    print(f"  After: {text}")

            except Exception as e:
                desc = rule.get('description', f'rule #{idx}')
                print(f"[ERROR] Mapping failed ({desc}): {e}")
                print(f"  Find: {find}")
                print(f"  Replace: {replace}")
                print(f"  Type: {rtype}")
                continue

        return text

    # ===== Validation =====
    def validate_input_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        errors, warnings = [], []
        for field in ['operation', 'shape_A', 'data_A']:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        if errors:
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        op = data['operation']
        if op not in self.geometry_ops.get('operations', {}):
            errors.append(f"Invalid operation: {op}")
        shape_A = data['shape_A']
        if shape_A not in self.geometry_shapes.get('shapes', {}):
            errors.append(f"Invalid shape A: {shape_A}")
        # requires two shapes?
        meta = self.geometry_ops.get('operations', {}).get(op, {})
        requires_two = meta.get('requires_two_shapes', False)
        if requires_two and not data.get('shape_B'):
            errors.append(f"Operation '{op}' requires shape_B")
        if (not requires_two) and data.get('shape_B'):
            warnings.append(f"Operation '{op}' does not require shape_B, it will be ignored")
        # compatibility check
        allowed = set(self.get_shapes_for_operation(op))
        if shape_A not in allowed:
            errors.append(f"Shape '{shape_A}' is not compatible with operation '{op}'")
        shape_B = data.get('shape_B')
        if shape_B:
            if shape_B not in allowed:
                errors.append(f"Shape '{shape_B}' is not compatible with operation '{op}'")
        # shape schema checks
        data_A = data['data_A'] if isinstance(data['data_A'], dict) else {}
        errors.extend(self._validate_shape_data(shape_A, data_A, 'A'))
        if data.get('data_B') and shape_B:
            errors.extend(self._validate_shape_data(shape_B, data['data_B'], 'B'))
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}

    def _validate_shape_data(self, shape: str, data: Dict[str, Any], group: str) -> List[str]:
        errors: List[str] = []
        if shape == 'Điểm':
            if 'point_input' not in data:
                errors.append(f"Missing 'point_input' for {shape} in group {group}")
        elif shape == 'Đường thẳng':
            req = ['line_A1' if group == 'A' else 'line_A2', 'line_X1' if group == 'A' else 'line_X2']
            for k in req:
                if k not in data:
                    errors.append(f"Missing '{k}' for {shape} in group {group}")
        elif shape == 'Mặt phẳng':
            for k in ['plane_a','plane_b','plane_c','plane_d']:
                if k not in data:
                    errors.append(f"Missing '{k}' for {shape} in group {group}")
        elif shape == 'Đường tròn':
            for k in ['circle_center','circle_radius']:
                if k not in data:
                    errors.append(f"Missing '{k}' for {shape} in group {group}")
        elif shape == 'Mặt cầu':
            for k in ['sphere_center','sphere_radius']:
                if k not in data:
                    errors.append(f"Missing '{k}' for {shape} in group {group}")
        return errors

    # ===== Processing =====
    def process_geometry(self, operation: str, shape_A: str, data_A: Dict[str, str],
                        shape_B: str = None, data_B: Dict[str, str] = None,
                        dimension_A: str = '3', dimension_B: str = '3',
                        version: str = None) -> Dict[str, Any]:
        self.current_operation = operation
        self.current_shape_A = shape_A
        self.current_shape_B = shape_B or ''
        self.dimension_A = dimension_A
        self.dimension_B = dimension_B
        self.current_version = version or self.main_config.get('default_version', 'fx799')
        
        self.results_A = self._process_shape_data(shape_A, data_A, 'A')
        self.results_B = []
        ops_meta = self.geometry_ops.get('operations', {}).get(operation, {})
        if shape_B and data_B and ops_meta.get('requires_two_shapes', False):
            self.results_B = self._process_shape_data(shape_B, data_B, 'B')
        keylog = self._generate_keylog()
        return {
            'operation': operation,
            'shape_A': shape_A,
            'shape_B': shape_B,
            'dimension_A': dimension_A,
            'dimension_B': dimension_B,
            'version': self.current_version,
            'encoded_A': self.results_A,
            'encoded_B': self.results_B,
            'keylog': keylog,
            'timestamp': datetime.now().isoformat()
        }

    def _process_shape_data(self, shape: str, data: Dict[str, str], group: str) -> List[str]:
        if shape == 'Điểm':
            return self._process_point_data(data, group)
        if shape == 'Đường thẳng':
            return self._process_line_data(data, group)
        if shape == 'Mặt phẳng':
            return self._process_plane_data(data)
        if shape == 'Đường tròn':
            return self._process_circle_data(data)
        if shape == 'Mặt cầu':
            return self._process_sphere_data(data)
        return []

    def _process_point_data(self, data: Dict[str, str], group: str) -> List[str]:
        point = data.get('point_input','')
        coords = point.split(',') if point else []
        dim = int(self.dimension_A if group=='A' else self.dimension_B)
        while len(coords) < dim:
            coords.append('0')
        return [self.encode_string(c.strip()) for c in coords[:dim]]

    def _process_line_data(self, data: Dict[str, str], group: str) -> List[str]:
        pk = 'line_A1' if group=='A' else 'line_A2'
        vk = 'line_X1' if group=='A' else 'line_X2'
        p = data.get(pk,'')
        v = data.get(vk,'')
        pc = p.split(',') if p else []
        vc = v.split(',') if v else []
        while len(pc) < 3: pc.append('0')
        while len(vc) < 3: vc.append('0')
        return [self.encode_string(x.strip()) for x in pc[:3]+vc[:3]]

    def _process_plane_data(self, data: Dict[str, str]) -> List[str]:
        coeffs = [data.get('plane_a','0'), data.get('plane_b','0'), data.get('plane_c','0'), data.get('plane_d','0')]
        return [self.encode_string(c.strip()) for c in coeffs]

    def _process_circle_data(self, data: Dict[str, str]) -> List[str]:
        center = data.get('circle_center','0,0')
        radius = data.get('circle_radius','1')
        cc = center.split(',') if center else ['0','0']
        while len(cc) < 2: cc.append('0')
        enc = [self.encode_string(c.strip()) for c in cc[:2]]
        enc.append(self.encode_string(radius.strip()))
        return enc

    def _process_sphere_data(self, data: Dict[str, str]) -> List[str]:
        center = data.get('sphere_center','0,0,0')
        radius = data.get('sphere_radius','1')
        cc = center.split(',') if center else ['0','0','0']
        while len(cc) < 3: cc.append('0')
        enc = [self.encode_string(c.strip()) for c in cc[:3]]
        enc.append(self.encode_string(radius.strip()))
        return enc

    # ===== Keylog building =====
    def _get_tcode(self, shape: str, group: str) -> str:
        info = self.geometry_shapes.get('shapes', {}).get(shape, {})
        return info.get(f'code_{group}', 'T0')

    def _get_shape_code(self, shape: str, group: str) -> str:
        info = self.geometry_shapes.get('shapes', {}).get(shape, {})
        code = info.get(f'shape_code_{group}')
        if isinstance(code, dict) and shape=='Điểm':
            dim = self.dimension_A if group=='A' else self.dimension_B
            return code.get(dim, code.get('3','113'))
        return str(code) if code else '00'

    def _values_str(self, group: str) -> str:
        vals = self.results_A if group=='A' else self.results_B
        return ('='.join(vals)+'=') if vals else ''

    def _generate_keylog(self) -> str:
        if not self.current_operation or not self.current_shape_A:
            return ''
        ops = self.geometry_ops.get('operations', {})
        meta = ops.get(self.current_operation, {})
        op_code = meta.get('code', '')
        ver_cfg = self.config_loader.get_version_config(self.current_version)
        prefix = ver_cfg.get('prefix','wj')
        
        t_a = self._get_tcode(self.current_shape_A,'A')
        shape_code_a = self._get_shape_code(self.current_shape_A,'A')
        vals_a = self._values_str('A')
        
        if not meta.get('requires_two_shapes', False):
            return f"{prefix}{shape_code_a}{vals_a}C{op_code}{t_a}="
        
        t_b = self._get_tcode(self.current_shape_B,'B') if self.current_shape_B else ''
        shape_code_b = self._get_shape_code(self.current_shape_B,'B') if self.current_shape_B else ''
        vals_b = self._values_str('B') if self.current_shape_B else ''
        return f"{prefix}{shape_code_a}{vals_a}C{shape_code_b}{vals_b}C{op_code}{t_a}R{t_b}="
