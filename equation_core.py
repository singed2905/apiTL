"""Equation processor core logic adapted from clone repo equation_service.py

Core features:
- Parse equation systems (2x2, 3x3, 4x4) 
- LaTeX-like input support (sqrt, sin, cos, pi, ^, fractions)
- Matrix solving with rank analysis
- Keylog encoding for Casio calculators
- Solutions classification (unique, infinite, no solution)
"""

import numpy as np
import math
from typing import List, Dict, Tuple, Optional, Any

class EquationProcessor:
    """Simplified equation processor for API usage"""
    
    def __init__(self):
        self.supported_variables = [2, 3, 4]
        self.supported_versions = ["fx799", "fx800", "fx801", "fx802", "fx803"]
    
    def process_single(self, operation: str, equations: List[str], version: str = "fx799") -> Dict[str, Any]:
        """Process single equation system"""
        try:
            # Parse operation to get variable count
            variables = self._extract_variable_count(operation)
            if variables not in self.supported_variables:
                return {
                    "success": False,
                    "error": f"Unsupported variable count: {variables}"
                }
            
            # Validate equations count
            if len(equations) < variables:
                return {
                    "success": False,
                    "error": f"Need at least {variables} equations for {variables} variables"
                }
            
            # Parse and solve
            A_matrix, b_vector, coeff_strings = self._parse_equations(equations[:variables], variables)
            solutions_info = self._solve_system(A_matrix, b_vector, variables)
            
            # Encode to keylog (simplified - would need full TL encoding from clone)
            encoded_coeffs = self._encode_coefficients(coeff_strings, variables, version)
            keylog = self._generate_keylog(encoded_coeffs, variables, version)
            
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
            return {
                "success": False,
                "error": str(e),
                "keylog": "",
                "solutions": "Error processing equation",
                "encoded_coefficients": []
            }
    
    def _extract_variable_count(self, operation: str) -> int:
        """Extract variable count from operation name"""
        if "2 ẩn" in operation:
            return 2
        elif "3 ẩn" in operation:
            return 3
        elif "4 ẩn" in operation:
            return 4
        return 2  # default
    
    def _parse_equations(self, equations: List[str], variables: int) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Parse equation strings into matrix form"""
        A_matrix = np.zeros((variables, variables))
        b_vector = np.zeros(variables)
        coeff_strings = []
        
        for i, eq_input in enumerate(equations):
            parts = [p.strip() for p in eq_input.split(',')]
            
            # Pad with zeros if insufficient coefficients
            if len(parts) < variables + 1:
                parts.extend(["0"] * (variables + 1 - len(parts)))
            
            # Store original strings for encoding
            coeff_strings.extend(parts[:variables + 1])
            
            # Parse to numbers for solving
            for j in range(variables):
                A_matrix[i, j] = self._safe_eval_number(parts[j])
            b_vector[i] = self._safe_eval_number(parts[variables])
        
        return A_matrix, b_vector, coeff_strings
    
    def _safe_eval_number(self, expr: str) -> float:
        """Safely evaluate LaTeX-like expression to number"""
        try:
            if not expr.strip():
                return 0.0
                
            # Replace LaTeX-like syntax
            expr_clean = (
                expr.replace('sqrt', 'math.sqrt')
                    .replace('sin', 'math.sin')
                    .replace('cos', 'math.cos') 
                    .replace('tan', 'math.tan')
                    .replace('log', 'math.log10')
                    .replace('ln', 'math.log')
                    .replace('pi', 'math.pi')
                    .replace('^', '**')
            )
            
            # Safe evaluation
            allowed = {"__builtins__": {}, "math": math}
            return float(eval(expr_clean, allowed))
            
        except Exception:
            try:
                return float(expr)
            except Exception:
                return 0.0
    
    def _solve_system(self, A_matrix: np.ndarray, b_vector: np.ndarray, variables: int) -> Dict[str, Any]:
        """Solve system with rank analysis"""
        try:
            # Rank analysis
            rank_A = np.linalg.matrix_rank(A_matrix)
            augmented = np.column_stack((A_matrix, b_vector))
            rank_augmented = np.linalg.matrix_rank(augmented)
            det = np.linalg.det(A_matrix)
            
            # Solve based on ranks
            if abs(det) > 1e-10:
                # Unique solution
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
                # Degenerate case
                if rank_A == rank_augmented:
                    solution_text = "Hệ có vô số nghiệm"
                else:
                    solution_text = "Hệ vô nghiệm (mâu thuẫn)"
            
            return {
                "text": solution_text,
                "rank_A": int(rank_A),
                "rank_augmented": int(rank_augmented),
                "determinant": float(det)
            }
            
        except Exception as e:
            return {
                "text": f"Lỗi giải hệ: {str(e)}",
                "rank_A": 0,
                "rank_augmented": 0,
                "determinant": 0.0
            }
    
    def _encode_coefficients(self, coeff_strings: List[str], variables: int, version: str) -> List[str]:
        """Encode coefficients to Casio format (simplified version)"""
        # This is a simplified encoder - full TL encoding would need the complete mapping from clone repo
        encoded = []
        for coeff in coeff_strings:
            # Basic encoding rules (simplified)
            encoded_coeff = self._encode_single_coefficient(coeff, version)
            encoded.append(encoded_coeff)
        return encoded
    
    def _encode_single_coefficient(self, coeff: str, version: str) -> str:
        """Basic coefficient encoding (placeholder - would need full TL mapping)"""
        if not coeff.strip():
            return "0"
        
        # Basic replacements
        encoded = coeff
        encoded = encoded.replace('sqrt', 's')
        encoded = encoded.replace('pi', 'p')
        encoded = encoded.replace('^', '')
        encoded = encoded.replace('(', '')
        encoded = encoded.replace(')', ')')
        
        return encoded
    
    def _generate_keylog(self, encoded_coeffs: List[str], variables: int, version: str) -> str:
        """Generate final keylog (simplified - would need full TL keylog generation)"""
        # This is a placeholder - full implementation would need the complete TL keylog logic
        keylog_parts = []
        
        # Add mode switch for equation mode
        keylog_parts.append("oi")  # MODE key for equations
        
        # Add coefficients in proper order
        for i, coeff in enumerate(encoded_coeffs):
            if i > 0:
                keylog_parts.append("=")  # separator
            keylog_parts.append(coeff)
        
        # Add solve command
        keylog_parts.append("=")  # equals to solve
        
        return "".join(keylog_parts)
