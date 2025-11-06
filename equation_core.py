"""Enhanced equation processor with TL-compatible keylog encoding using clone repo configs"""

import numpy as np
import math
import json
import os
import re
from typing import List, Dict, Tuple, Optional, Any

class EquationProcessor:
    """Enhanced equation processor with TL keylog encoding from clone repo"""
    
    def __init__(self):
        self.supported_variables = [2, 3, 4]
        self.supported_versions = ["fx799", "fx800", "fx801", "fx802", "fx803"]
        self.config_dir = os.path.join(os.path.dirname(__file__), 'config')
        
        # Load configs from clone repo
        self.prefixes = self._load_prefixes()
        self.mappings = self._load_mappings()
    
    def _load_prefixes(self) -> Dict:
        """Load equation prefixes from config"""
        try:
            path = os.path.join(self.config_dir, 'equation_prefixes.json')
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Cannot load equation_prefixes.json: {e}")
            return {
                "global_defaults": {"2": "w912", "3": "w913", "4": "w914"},
                "versions": {
                    "fx799": {"equation": {"2": "w912", "3": "w913", "4": "w914"}}
                }
            }
    
    def _load_mappings(self) -> List[Dict]:
        """Load LaTeX to keylog mappings"""
        try:
            path = os.path.join(self.config_dir, 'equation_mapping.json')
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('mappings', [])
        except Exception as e:
            print(f"[WARN] Cannot load equation_mapping.json: {e}")
            return []
    
    def process_single(self, operation: str, equations: List[str], version: str = "fx799") -> Dict[str, Any]:
        """Process single equation system with TL encoding"""
        try:
            variables = self._extract_variable_count(operation)
            if variables not in self.supported_variables:
                return {"success": False, "error": f"Unsupported variable count: {variables}"}
            
            if len(equations) < variables:
                return {"success": False, "error": f"Need at least {variables} equations for {variables} variables"}
            
            # Parse and solve
            A_matrix, b_vector, coeff_strings = self._parse_equations(equations[:variables], variables)
            solutions_info = self._solve_system(A_matrix, b_vector, variables)
            
            # TL encoding with actual config
            encoded_coeffs = self._encode_coefficients_tl(coeff_strings, variables, version)
            keylog = self._generate_keylog_tl(encoded_coeffs, variables, version)
            
            return {
                "success": True,
                "keylog": keylog,
                "solutions": solutions_info["text"],
                "encoded_coefficients": encoded_coeffs,
                "matrix_info": {
                    "rank_A": solutions_info["rank_A"],
                    "rank_augmented": solutions_info["rank_augmented"],
                    "determinant": solutions_info["determinant"]
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "keylog": "", "solutions": "Error processing equation", "encoded_coefficients": []}
    
    def _extract_variable_count(self, operation: str) -> int:
        if "2 ẩn" in operation: return 2
        elif "3 ẩn" in operation: return 3
        elif "4 ẩn" in operation: return 4
        return 2
    
    def _parse_equations(self, equations: List[str], variables: int) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        A_matrix = np.zeros((variables, variables))
        b_vector = np.zeros(variables)
        coeff_strings = []
        
        for i, eq_input in enumerate(equations):
            parts = [p.strip() for p in eq_input.split(',')]
            if len(parts) < variables + 1:
                parts.extend(["0"] * (variables + 1 - len(parts)))
            coeff_strings.extend(parts[:variables + 1])
            for j in range(variables):
                A_matrix[i, j] = self._safe_eval_number(parts[j])
            b_vector[i] = self._safe_eval_number(parts[variables])
        return A_matrix, b_vector, coeff_strings
    
    def _safe_eval_number(self, expr: str) -> float:
        try:
            if not expr.strip(): return 0.0
            expr_clean = (expr.replace('sqrt', 'math.sqrt').replace('sin', 'math.sin').replace('cos', 'math.cos').replace('tan', 'math.tan').replace('log', 'math.log10').replace('ln', 'math.log').replace('pi', 'math.pi').replace('^', '**'))
            return float(eval(expr_clean, {"__builtins__": {}, "math": math}))
        except Exception:
            try: return float(expr)
            except Exception: return 0.0
    
    def _solve_system(self, A_matrix: np.ndarray, b_vector: np.ndarray, variables: int) -> Dict[str, Any]:
        try:
            rank_A = np.linalg.matrix_rank(A_matrix)
            augmented = np.column_stack((A_matrix, b_vector))
            rank_augmented = np.linalg.matrix_rank(augmented)
            det = np.linalg.det(A_matrix)
            
            if abs(det) > 1e-10:
                solutions = np.linalg.solve(A_matrix, b_vector)
                variables_names = ['x', 'y', 'z', 't'][:variables]
                solution_parts = []
                for i, sol in enumerate(solutions):
                    if abs(sol - round(sol)) < 1e-10:
                        solution_parts.append(f"{variables_names[i]} = {int(round(sol))}")
                    else:
                        solution_parts.append(f"{variables_names[i]} = {sol:.4f}")
                solution_text = "; ".join(solution_parts)
            else:
                if rank_A == rank_augmented:
                    solution_text = "Hệ có vô số nghiệm"
                else:
                    solution_text = "Hệ vô nghiệm (mâu thuẫn)"
            
            return {"text": solution_text, "rank_A": int(rank_A), "rank_augmented": int(rank_augmented), "determinant": float(det)}
        except Exception as e:
            return {"text": f"Lỗi giải hệ: {str(e)}", "rank_A": 0, "rank_augmented": 0, "determinant": 0.0}
    
    def _encode_coefficients_tl(self, coeff_strings: List[str], variables: int, version: str) -> List[str]:
        """Encode using TL mapping rules from clone repo config"""
        encoded = []
        for coeff in coeff_strings:
            encoded_coeff = self._apply_tl_mappings(coeff.strip())
            encoded.append(encoded_coeff)
        return encoded
    
    def _apply_tl_mappings(self, text: str) -> str:
        """Apply LaTeX to keylog mappings from config"""
        if not text: return "0"
        result = text
        
        # Apply each mapping rule
        for mapping in self.mappings:
            try:
                if mapping.get('type') == 'regex':
                    pattern = mapping['find']
                    replacement = mapping['replace']
                    result = re.sub(pattern, replacement, result)
            except Exception as e:
                print(f"[WARN] Mapping rule failed: {mapping.get('description', 'unknown')}: {e}")
        
        return result
    
    def _generate_keylog_tl(self, encoded_coeffs: List[str], variables: int, version: str) -> str:
        """Generate TL-compatible keylog using prefixes from clone repo"""
        try:
            # Get prefix for this version and variable count
            prefix = self._get_equation_prefix(variables, version)
            
            keylog_parts = [prefix]
            
            # Add coefficients separated by '='
            for i, coeff in enumerate(encoded_coeffs):
                if i > 0:
                    keylog_parts.append("=")
                keylog_parts.append(coeff)
            
            # Add final solve command
            keylog_parts.append("=")
            
            return "".join(keylog_parts)
            
        except Exception as e:
            print(f"[WARN] Keylog generation failed: {e}")
            return f"ERROR_KEYLOG_{version}_{variables}"
    
    def _get_equation_prefix(self, variables: int, version: str) -> str:
        """Get equation mode prefix from config"""
        try:
            var_str = str(variables)
            # Try version-specific first
            if version in self.prefixes.get('versions', {}):
                version_config = self.prefixes['versions'][version]
                if 'equation' in version_config and var_str in version_config['equation']:
                    return version_config['equation'][var_str]
            
            # Fallback to global defaults
            if var_str in self.prefixes.get('global_defaults', {}):
                return self.prefixes['global_defaults'][var_str]
            
            # Final fallback
            return f"w91{variables}"
            
        except Exception as e:
            print(f"[WARN] Prefix lookup failed: {e}")
            return f"w91{variables}"
