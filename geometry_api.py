from typing import Dict, Any, List, Union, Optional
from datetime import datetime
import re
import json

class GeometryAPI:
    """API wrapper for geometry functionality from ConvertKeylogApp"""
    
    def __init__(self):
        # Initialize geometry mappings and configurations
        self.geometry_data = self._init_geometry_data()
        self.mapping_rules = self._init_mapping_rules()
        self.version_configs = self._init_version_configs()
        
        # Current processing state
        self.current_operation = ""
        self.current_shape_A = ""
        self.current_shape_B = ""
        self.dimension_A = "3"
        self.dimension_B = "3"
        self.current_version = "fx799"
        
        # Processing results storage
        self.results_A = []
        self.results_B = []
    
    def _init_geometry_data(self) -> Dict[str, Any]:
        """Initialize geometry data mappings"""
        return {
            "operations": {
                "Tương giao": {"code": "qT2", "requires_two_shapes": True},
                "Khoảng cách": {"code": "qT3", "requires_two_shapes": True},
                "Diện tích": {"code": "qT4", "requires_two_shapes": False},
                "Thể tích": {"code": "qT5", "requires_two_shapes": False},
                "PT đường thẳng": {"code": "qT6", "requires_two_shapes": True}
            },
            "shapes": {
                "Điểm": {
                    "code_A": "T1", "code_B": "T2",
                    "shape_code_A": {"2": "112", "3": "113"},
                    "shape_code_B": {"2": "qT11T122", "3": "qT11T123"},
                    "params": {"2": 2, "3": 3}
                },
                "Đường thẳng": {
                    "code_A": "T4", "code_B": "T5",
                    "shape_code_A": "21", "shape_code_B": "qT12T12",
                    "params": 6  # point(3) + vector(3)
                },
                "Mặt phẳng": {
                    "code_A": "T7", "code_B": "T8", 
                    "shape_code_A": "31", "shape_code_B": "qT13T12",
                    "params": 4  # a,b,c,d coefficients
                },
                "Đường tròn": {
                    "code_A": "Tz", "code_B": "Tx",
                    "shape_code_A": "41", "shape_code_B": "qT14T12",
                    "params": 3  # center(2) + radius(1)
                },
                "Mặt cầu": {
                    "code_A": "Tj", "code_B": "Tk",
                    "shape_code_A": "51", "shape_code_B": "qT15T12",
                    "params": 4  # center(3) + radius(1)
                }
            },
            "operation_filters": {
                "Khoảng cách": ["Điểm", "Đường thẳng", "Mặt phẳng"],
                "Diện tích": ["Đường tròn", "Mặt cầu"],
                "Thể tích": ["Mặt cầu"],
                "PT đường thẳng": ["Điểm"],
                "Tương giao": ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]
            }
        }
    
    def _init_mapping_rules(self) -> List[Dict[str, str]]:
        """Initialize LaTeX to calculator mapping rules"""
        return [
            {"find": r"\\frac\{([^{}]+)\}\{([^{}]+)\}", "replace": r"\1a\2", "type": "regex"},
            {"find": r"\\-", "replace": "p", "type": "regex"},
            {"find": r"\\\*", "replace": "O", "type": "regex"},
            {"find": r"\\/", "replace": "P", "type": "regex"},
            {"find": r"\\sqrt\{", "replace": "s", "type": "regex"},
            {"find": r"sqrt\{", "replace": "s", "type": "regex"},
            {"find": r"\\sin\(", "replace": "j(", "type": "regex"},
            {"find": r"sin\(", "replace": "j(", "type": "regex"},
            {"find": r"\\cos\(", "replace": "k(", "type": "regex"},
            {"find": r"cos\(", "replace": "k(", "type": "regex"},
            {"find": r"\\tan\(", "replace": "l(", "type": "regex"},
            {"find": r"tan\(", "replace": "l(", "type": "regex"},
            {"find": r"\\ln\(", "replace": "h(", "type": "regex"},
            {"find": r"ln\(", "replace": "h(", "type": "regex"},
            {"find": r"\\}", "replace": ")", "type": "regex"},
            {"find": r"\\{", "replace": "(", "type": "regex"},
            {"find": r"\\\^", "replace": "^", "type": "regex"},
            {"find": "_", "replace": "_", "type": "literal"}
        ]
    
    def _init_version_configs(self) -> Dict[str, Dict[str, str]]:
        """Initialize calculator version configurations"""
        return {
            "fx799": {"prefix": "wj", "name": "Casio fx-799"},
            "fx800": {"prefix": "wj", "name": "Casio fx-800"},
            "fx801": {"prefix": "wj", "name": "Casio fx-801"},
            "fx802": {"prefix": "wj", "name": "Casio fx-802"},
            "fx803": {"prefix": "wj", "name": "Casio fx-803"}
        }
    
    def get_available_shapes(self) -> List[str]:
        """Get list of available geometric shapes"""
        return list(self.geometry_data["shapes"].keys())
    
    def get_available_operations(self) -> List[str]:
        """Get list of available operations"""
        return list(self.geometry_data["operations"].keys())
    
    def get_shapes_for_operation(self, operation: str) -> List[str]:
        """Get available shapes for a specific operation"""
        if operation in self.geometry_data["operation_filters"]:
            return self.geometry_data["operation_filters"][operation]
        return self.get_available_shapes()
    
    def encode_string(self, input_string: str) -> str:
        """Encode string using LaTeX to calculator mapping rules"""
        if not input_string:
            return ""
        
        input_string = input_string.replace(" ", "")
        result = input_string
        
        # Apply mapping rules
        for rule in self.mapping_rules:
            find_pattern = rule["find"]
            replace_pattern = rule["replace"]
            rule_type = rule["type"]
            
            try:
                if rule_type == "regex":
                    result = re.sub(find_pattern, replace_pattern, result)
                else:
                    result = result.replace(find_pattern, replace_pattern)
            except Exception as e:
                print(f"Encoding error with pattern '{find_pattern}': {e}")
                continue
        
        return result
    
    def validate_input_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data for geometry processing"""
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['operation', 'shape_A', 'data_A']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        operation = data['operation']
        shape_A = data['shape_A']
        
        # Validate operation
        if operation not in self.geometry_data["operations"]:
            errors.append(f"Invalid operation: {operation}")
        
        # Validate shapes
        if shape_A not in self.geometry_data["shapes"]:
            errors.append(f"Invalid shape A: {shape_A}")
        
        # Check if operation requires two shapes
        if operation in self.geometry_data["operations"]:
            requires_two = self.geometry_data["operations"][operation]["requires_two_shapes"]
            if requires_two and ('shape_B' not in data or not data['shape_B']):
                errors.append(f"Operation '{operation}' requires shape_B")
            elif not requires_two and 'shape_B' in data and data['shape_B']:
                warnings.append(f"Operation '{operation}' does not require shape_B, it will be ignored")
        
        # Validate shape compatibility with operation
        available_shapes = self.get_shapes_for_operation(operation)
        if shape_A not in available_shapes:
            errors.append(f"Shape '{shape_A}' is not compatible with operation '{operation}'")
        
        if 'shape_B' in data and data['shape_B']:
            if data['shape_B'] not in available_shapes:
                errors.append(f"Shape '{shape_B}' is not compatible with operation '{operation}'")
        
        # Validate data structure for shapes
        data_A = data['data_A']
        if isinstance(data_A, dict):
            shape_errors = self._validate_shape_data(shape_A, data_A, 'A')
            errors.extend(shape_errors)
        
        if 'data_B' in data and data['data_B']:
            data_B = data['data_B']
            if isinstance(data_B, dict) and 'shape_B' in data:
                shape_errors = self._validate_shape_data(data['shape_B'], data_B, 'B')
                errors.extend(shape_errors)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_shape_data(self, shape: str, data: Dict[str, Any], group: str) -> List[str]:
        """Validate data structure for specific shape"""
        errors = []
        
        if shape == "Điểm":
            if 'point_input' not in data:
                errors.append(f"Missing 'point_input' for {shape} in group {group}")
        elif shape == "Đường thẳng":
            required = ['line_A1' if group == 'A' else 'line_A2', 'line_X1' if group == 'A' else 'line_X2']
            for req in required:
                if req not in data:
                    errors.append(f"Missing '{req}' for {shape} in group {group}")
        elif shape == "Mặt phẳng":
            required = ['plane_a', 'plane_b', 'plane_c', 'plane_d']
            for req in required:
                if req not in data:
                    errors.append(f"Missing '{req}' for {shape} in group {group}")
        elif shape == "Đường tròn":
            required = ['circle_center', 'circle_radius']
            for req in required:
                if req not in data:
                    errors.append(f"Missing '{req}' for {shape} in group {group}")
        elif shape == "Mặt cầu":
            required = ['sphere_center', 'sphere_radius']
            for req in required:
                if req not in data:
                    errors.append(f"Missing '{req}' for {shape} in group {group}")
        
        return errors
    
    def get_input_template(self, shape_A: str, shape_B: str = None) -> Dict[str, Any]:
        """Get input template structure for shapes"""
        template = {
            'operation': 'string - one of: ' + ', '.join(self.get_available_operations()),
            'shape_A': shape_A,
            'data_A': self._get_shape_template(shape_A, 'A'),
            'dimension_A': '2 or 3 (for points)',
            'version': 'fx799, fx800, fx801, fx802, fx803 (default: fx799)'
        }
        
        if shape_B:
            template['shape_B'] = shape_B
            template['data_B'] = self._get_shape_template(shape_B, 'B')
            template['dimension_B'] = '2 or 3 (for points)'
        
        return template
    
    def _get_shape_template(self, shape: str, group: str) -> Dict[str, str]:
        """Get data template for specific shape"""
        if shape == "Điểm":
            return {
                'point_input': 'string - coordinates separated by comma, e.g., "1,2,3"'
            }
        elif shape == "Đường thẳng":
            line_key = 'line_A1' if group == 'A' else 'line_A2'
            vector_key = 'line_X1' if group == 'A' else 'line_X2'
            return {
                line_key: 'string - point coordinates, e.g., "1,2,3"',
                vector_key: 'string - direction vector, e.g., "1,0,0"'
            }
        elif shape == "Mặt phẳng":
            return {
                'plane_a': 'string - coefficient a',
                'plane_b': 'string - coefficient b', 
                'plane_c': 'string - coefficient c',
                'plane_d': 'string - coefficient d'
            }
        elif shape == "Đường tròn":
            return {
                'circle_center': 'string - center coordinates, e.g., "0,0"',
                'circle_radius': 'string - radius value'
            }
        elif shape == "Mặt cầu":
            return {
                'sphere_center': 'string - center coordinates, e.g., "0,0,0"', 
                'sphere_radius': 'string - radius value'
            }
        return {}
    
    def process_geometry(self, operation: str, shape_A: str, data_A: Dict[str, str],
                        shape_B: str = None, data_B: Dict[str, str] = None,
                        dimension_A: str = '3', dimension_B: str = '3',
                        version: str = 'fx799') -> Dict[str, Any]:
        """Process single geometry calculation"""
        
        # Set current state
        self.current_operation = operation
        self.current_shape_A = shape_A
        self.current_shape_B = shape_B or ""
        self.dimension_A = dimension_A
        self.dimension_B = dimension_B  
        self.current_version = version
        
        # Process shape A
        self.results_A = self._process_shape_data(shape_A, data_A, 'A')
        
        # Process shape B if needed
        self.results_B = []
        if shape_B and data_B and operation not in ["Diện tích", "Thể tích"]:
            self.results_B = self._process_shape_data(shape_B, data_B, 'B')
        
        # Generate final keylog result
        keylog = self._generate_keylog()
        
        return {
            'operation': operation,
            'shape_A': shape_A,
            'shape_B': shape_B,
            'dimension_A': dimension_A,
            'dimension_B': dimension_B,
            'version': version,
            'encoded_A': self.results_A,
            'encoded_B': self.results_B,
            'keylog': keylog,
            'timestamp': datetime.now().isoformat()
        }
    
    def _process_shape_data(self, shape: str, data: Dict[str, str], group: str) -> List[str]:
        """Process shape data and return encoded values"""
        if shape == "Điểm":
            return self._process_point_data(data, group)
        elif shape == "Đường thẳng":
            return self._process_line_data(data, group)
        elif shape == "Mặt phẳng":
            return self._process_plane_data(data)
        elif shape == "Đường tròn":
            return self._process_circle_data(data)
        elif shape == "Mặt cầu":
            return self._process_sphere_data(data)
        return []
    
    def _process_point_data(self, data: Dict[str, str], group: str) -> List[str]:
        """Process point data"""
        point_input = data.get('point_input', '')
        coords = point_input.split(',') if point_input else []
        
        dimension = int(self.dimension_A if group == 'A' else self.dimension_B)
        while len(coords) < dimension:
            coords.append('0')
        
        return [self.encode_string(coord.strip()) for coord in coords[:dimension]]
    
    def _process_line_data(self, data: Dict[str, str], group: str) -> List[str]:
        """Process line data"""
        point_key = 'line_A1' if group == 'A' else 'line_A2'
        vector_key = 'line_X1' if group == 'A' else 'line_X2'
        
        point_input = data.get(point_key, '')
        vector_input = data.get(vector_key, '')
        
        point_coords = point_input.split(',') if point_input else []
        vector_coords = vector_input.split(',') if vector_input else []
        
        # Ensure 3 coordinates each
        while len(point_coords) < 3:
            point_coords.append('0')
        while len(vector_coords) < 3:
            vector_coords.append('0')
        
        # Encode point + vector coordinates
        encoded = []
        for coord in point_coords[:3]:
            encoded.append(self.encode_string(coord.strip()))
        for coord in vector_coords[:3]:
            encoded.append(self.encode_string(coord.strip()))
        
        return encoded
    
    def _process_plane_data(self, data: Dict[str, str]) -> List[str]:
        """Process plane data"""
        coeffs = [
            data.get('plane_a', '0'),
            data.get('plane_b', '0'), 
            data.get('plane_c', '0'),
            data.get('plane_d', '0')
        ]
        return [self.encode_string(coeff.strip()) for coeff in coeffs]
    
    def _process_circle_data(self, data: Dict[str, str]) -> List[str]:
        """Process circle data"""
        center_input = data.get('circle_center', '0,0')
        radius_input = data.get('circle_radius', '1')
        
        center_coords = center_input.split(',') if center_input else ['0', '0']
        while len(center_coords) < 2:
            center_coords.append('0')
        
        encoded = []
        for coord in center_coords[:2]:
            encoded.append(self.encode_string(coord.strip()))
        encoded.append(self.encode_string(radius_input.strip()))
        
        return encoded
    
    def _process_sphere_data(self, data: Dict[str, str]) -> List[str]:
        """Process sphere data"""
        center_input = data.get('sphere_center', '0,0,0')
        radius_input = data.get('sphere_radius', '1')
        
        center_coords = center_input.split(',') if center_input else ['0', '0', '0']
        while len(center_coords) < 3:
            center_coords.append('0')
        
        encoded = []
        for coord in center_coords[:3]:
            encoded.append(self.encode_string(coord.strip()))
        encoded.append(self.encode_string(radius_input.strip()))
        
        return encoded
    
    def _generate_keylog(self) -> str:
        """Generate final keylog string"""
        if not self.current_operation or not self.current_shape_A:
            return ""
        
        # Get operation code
        operation_code = self.geometry_data["operations"][self.current_operation]["code"]
        
        # Get version prefix
        version_config = self.version_configs.get(self.current_version, self.version_configs["fx799"])
        prefix = version_config["prefix"]
        
        # Get T-codes
        tcode_A = self._get_tcode(self.current_shape_A, 'A')
        tcode_B = self._get_tcode(self.current_shape_B, 'B') if self.current_shape_B else ""
        
        # Get shape codes and encoded values
        shape_code_A = self._get_shape_code(self.current_shape_A, 'A')
        encoded_values_A = self._get_encoded_values_string('A')
        
        # Build final keylog
        if self.current_operation in ["Diện tích", "Thể tích"]:
            # Single shape operations
            keylog = f"{prefix}{shape_code_A}{encoded_values_A}C{operation_code}{tcode_A}="
        else:
            # Two shape operations
            shape_code_B = self._get_shape_code(self.current_shape_B, 'B')
            encoded_values_B = self._get_encoded_values_string('B')
            keylog = f"{prefix}{shape_code_A}{encoded_values_A}C{shape_code_B}{encoded_values_B}C{operation_code}{tcode_A}R{tcode_B}="
        
        return keylog
    
    def _get_tcode(self, shape: str, group: str) -> str:
        """Get T-code for shape and group"""
        if not shape or shape not in self.geometry_data["shapes"]:
            return "T0"
        
        shape_info = self.geometry_data["shapes"][shape]
        return shape_info.get(f"code_{group}", "T0")
    
    def _get_shape_code(self, shape: str, group: str) -> str:
        """Get shape code for keylog"""
        if not shape or shape not in self.geometry_data["shapes"]:
            return "00"
        
        shape_info = self.geometry_data["shapes"][shape]
        shape_code = shape_info.get(f"shape_code_{group}")
        
        if isinstance(shape_code, dict) and shape == "Điểm":
            dimension = self.dimension_A if group == 'A' else self.dimension_B
            return shape_code.get(dimension, shape_code.get("3", "113"))
        
        return str(shape_code) if shape_code else "00"
    
    def _get_encoded_values_string(self, group: str) -> str:
        """Get encoded values as string for keylog"""
        results = self.results_A if group == 'A' else self.results_B
        if not results:
            return ""
        
        return '='.join(results) + '='
    
    def process_batch(self, calculations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple geometry calculations"""
        results = []
        
        for i, calc in enumerate(calculations):
            try:
                # Validate individual calculation
                validation = self.validate_input_data(calc)
                if not validation['valid']:
                    results.append({
                        'index': i,
                        'status': 'error',
                        'errors': validation['errors'],
                        'warnings': validation.get('warnings', [])
                    })
                    continue
                
                # Process calculation
                result = self.process_geometry(
                    operation=calc['operation'],
                    shape_A=calc['shape_A'],
                    data_A=calc['data_A'],
                    shape_B=calc.get('shape_B'),
                    data_B=calc.get('data_B'),
                    dimension_A=calc.get('dimension_A', '3'),
                    dimension_B=calc.get('dimension_B', '3'),
                    version=calc.get('version', 'fx799')
                )
                
                result['index'] = i
                result['status'] = 'success'
                results.append(result)
                
            except Exception as e:
                results.append({
                    'index': i,
                    'status': 'error',
                    'message': str(e)
                })
        
        return results
