import pandas as pd
import json
import os
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import tempfile

class EquationExcelProcessor:
    """Excel Processor for Equation Mode - ConvertKeylogApp API"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.mapping = self._load_equation_mapping()
        self.large_file_threshold_mb = 20
        self.large_file_threshold_rows = 10000
    
    def _load_equation_mapping(self) -> Dict:
        """Load Excel mapping configuration for equation mode"""
        return {
            "Hệ phương trình 2 ẩn": {
                "required_columns": ["a11", "a12", "c1", "a21", "a22", "c2"],
                "variables_count": 2,
                "equations_count": 2
            },
            "Hệ phương trình 3 ẩn": {
                "required_columns": ["a11", "a12", "a13", "c1", "a21", "a22", "a23", "c2", "a31", "a32", "a33", "c3"],
                "variables_count": 3,
                "equations_count": 3
            },
            "Hệ phương trình 4 ẩn": {
                "required_columns": ["a11", "a12", "a13", "a14", "c1", "a21", "a22", "a23", "a24", "c2", 
                                   "a31", "a32", "a33", "a34", "c3", "a41", "a42", "a43", "a44", "c4"],
                "variables_count": 4,
                "equations_count": 4
            }
        }
    
    def read_excel_data(self, file_path: str) -> pd.DataFrame:
        """Read Excel file and normalize data"""
        try:
            df = pd.read_excel(file_path)
            # Normalize column names (remove extra spaces)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            raise Exception(f"Không thể đọc file Excel: {str(e)}")
    
    def validate_excel_structure(self, df: pd.DataFrame, operation: str) -> Tuple[bool, List[str]]:
        """Validate Excel structure against selected equation operation"""
        missing_columns = []
        
        if operation not in self.mapping:
            return False, [f"Operation '{operation}' không được hỗ trợ"]
        
        required_cols = self.mapping[operation]['required_columns']
        for col in required_cols:
            if col not in df.columns:
                missing_columns.append(col)
        
        return len(missing_columns) == 0, missing_columns
    
    def extract_equation_data(self, row: pd.Series, operation: str) -> List[str]:
        """Extract equation coefficients from Excel row"""
        operation_config = self.mapping.get(operation, {})
        variables_count = operation_config.get('variables_count', 2)
        equations_count = operation_config.get('equations_count', 2)
        
        equations = []
        
        for eq_idx in range(1, equations_count + 1):
            coefficients = []
            
            # Extract coefficients for this equation
            for var_idx in range(1, variables_count + 1):
                coeff_col = f"a{eq_idx}{var_idx}"
                if coeff_col in row.index:
                    value = row[coeff_col]
                    if pd.isna(value):
                        coefficients.append("0")
                    else:
                        coefficients.append(str(value).strip())
                else:
                    coefficients.append("0")
            
            # Add constant term
            const_col = f"c{eq_idx}"
            if const_col in row.index:
                value = row[const_col]
                if pd.isna(value):
                    coefficients.append("0")
                else:
                    coefficients.append(str(value).strip())
            else:
                coefficients.append("0")
            
            # Join coefficients with comma
            equation_str = ",".join(coefficients)
            equations.append(equation_str)
        
        return equations
    
    def process_excel_equations(self, file_path: str, operation: str, version: str = "fx799", 
                              progress_callback: callable = None) -> Tuple[int, int, str]:
        """Process Excel file with equation data"""
        try:
            from equation_core import EquationProcessor
            
            # Read Excel data
            df = self.read_excel_data(file_path)
            
            # Validate structure
            is_valid, missing_cols = self.validate_excel_structure(df, operation)
            if not is_valid:
                raise Exception(f"Cấu trúc Excel không hợp lệ. Thiếu cột: {', '.join(missing_cols)}")
            
            # Initialize equation processor
            equation_processor = EquationProcessor()
            
            # Process each row
            results = []
            processed_count = 0
            error_count = 0
            
            for index, row in df.iterrows():
                try:
                    # Extract equation data from row
                    equations = self.extract_equation_data(row, operation)
                    
                    # Check if row has data
                    if not any(eq.replace(',', '').replace('0', '').strip() for eq in equations):
                        continue  # Skip empty rows
                    
                    # Process equation
                    result = equation_processor.process_single(operation, equations, version)
                    
                    if result.get('success'):
                        results.append(result['keylog'])
                        processed_count += 1
                    else:
                        results.append(f"ERROR: {result.get('error', 'Unknown error')}")
                        error_count += 1
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(index + 1, len(df))
                
                except Exception as e:
                    results.append(f"ERROR: {str(e)}")
                    error_count += 1
            
            # Create output file with results
            output_path = self.export_equation_results(df, results, operation, version)
            
            return processed_count, error_count, output_path
            
        except Exception as e:
            raise Exception(f"Lỗi xử lý Excel equations: {str(e)}")
    
    def export_equation_results(self, original_df: pd.DataFrame, encoded_results: List[str], 
                               operation: str, version: str) -> str:
        """Export equation results with Excel formatting"""
        try:
            result_df = original_df.copy()
            
            # Add results column
            result_df['Keylog_Result'] = encoded_results
            result_df['Operation'] = operation
            result_df['Version'] = version
            result_df['Processed_Time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Generate output filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"equation_results_{timestamp}.xlsx"
            output_path = os.path.join(tempfile.gettempdir(), output_filename)
            
            # Export with formatting
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                result_df.to_excel(writer, index=False, sheet_name='Results')
                
                # Format the worksheet
                worksheet = writer.sheets['Results']
                self._format_results_worksheet(worksheet, result_df)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Không thể xuất file kết quả: {str(e)}")
    
    def _format_results_worksheet(self, worksheet, df):
        """Format Excel worksheet with colors and fonts"""
        try:
            from openpyxl.styles import Font, PatternFill
            from openpyxl.utils import get_column_letter
            
            # Header formatting
            header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='2E86AB', end_color='2E86AB', fill_type='solid')
            
            # Data formatting
            data_font = Font(name='Arial', size=10)
            result_font = Font(name='Arial', size=10, bold=True, color='2E7D32')
            
            # Apply header formatting
            for col in range(1, len(df.columns) + 1):
                cell = worksheet.cell(row=1, column=col)
                cell.font = header_font
                cell.fill = header_fill
            
            # Find keylog column index
            keylog_col_idx = None
            for idx, col_name in enumerate(df.columns):
                if 'Keylog_Result' in str(col_name):
                    keylog_col_idx = idx
                    break
            
            # Apply data formatting - limit to first 1000 rows for performance
            max_format_rows = min(len(df) + 2, 1000)
            for row in range(2, max_format_rows):
                for col in range(1, len(df.columns) + 1):
                    cell = worksheet.cell(row=row, column=col)
                    
                    # Special formatting for result column
                    if keylog_col_idx is not None and col == keylog_col_idx + 1:
                        cell.font = result_font
                    else:
                        cell.font = data_font
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                
                # Check only first 50 rows for performance
                for i, cell in enumerate(column):
                    if i > 50:
                        break
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
        except Exception as e:
            print(f"Warning: Could not format worksheet: {e}")
    
    def create_equation_template(self, operation: str, output_path: str) -> str:
        """Create Excel template for equation data input"""
        try:
            if operation not in self.mapping:
                raise Exception(f"Operation '{operation}' không được hỗ trợ")
            
            operation_config = self.mapping[operation]
            required_cols = operation_config['required_columns']
            
            # Create sample data
            template_data = {}
            for col in required_cols:
                template_data[col] = self._get_equation_sample_data(col)
            
            # Add keylog result column
            template_data['Keylog_Result'] = [''] * len(next(iter(template_data.values())))
            
            # Create DataFrame
            df = pd.DataFrame(template_data)
            
            # Export template
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Template')
                
                # Format template
                worksheet = writer.sheets['Template']
                self._format_template_worksheet(worksheet, df, operation)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Không thể tạo template: {str(e)}")
    
    def _get_equation_sample_data(self, column: str) -> List[str]:
        """Generate sample data for equation template"""
        if column.startswith('a'):
            # Coefficient columns
            return ['1', '2', '0', '1']
        elif column.startswith('c'):
            # Constant columns
            return ['5', '7', '3', '10']
        return ['', '', '', '']
    
    def _format_template_worksheet(self, worksheet, df, operation):
        """Format template worksheet with instructions"""
        try:
            from openpyxl.styles import Font, PatternFill
            from openpyxl.utils import get_column_letter
            
            # Header formatting
            header_font = Font(name='Arial', size=12, bold=True, color='FFFFFF')
            header_fill = PatternFill(start_color='4CAF50', end_color='4CAF50', fill_type='solid')
            
            # Apply header formatting
            for col in range(1, len(df.columns) + 1):
                cell = worksheet.cell(row=1, column=col)
                cell.font = header_font
                cell.fill = header_fill
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 15)
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
        except Exception as e:
            print(f"Warning: Could not format template: {e}")
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about Excel file"""
        try:
            df = self.read_excel_data(file_path)
            file_name = os.path.basename(file_path)
            
            return {
                'file_name': file_name,
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'file_size': os.path.getsize(file_path),
                'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'first_few_rows': df.head(3).to_dict('records') if len(df) > 0 else []
            }
        except Exception as e:
            raise Exception(f"Không thể đọc thông tin file: {str(e)}")
    
    def validate_data_quality(self, df: pd.DataFrame, operation: str) -> Dict[str, Any]:
        """Validate data quality in Excel file for equations"""
        quality_info = {
            'valid': True,
            'total_rows': len(df),
            'rows_with_data': 0,
            'rows_with_errors': 0,
            'missing_columns': [],
            'data_issues': []
        }
        
        # Check structure first
        is_valid, missing_cols = self.validate_excel_structure(df, operation)
        if not is_valid:
            quality_info['valid'] = False
            quality_info['missing_columns'] = missing_cols
            return quality_info
        
        # Check rows for data quality
        for row_index in range(len(df)):
            row = df.iloc[row_index]
            has_data = False
            row_issues = []
            
            # Extract equation data
            try:
                equations = self.extract_equation_data(row, operation)
                if any(eq.replace(',', '').replace('0', '').strip() for eq in equations):
                    has_data = True
                    
                    # Validate equation coefficients
                    for eq_idx, eq in enumerate(equations):
                        coeffs = eq.split(',')
                        for coeff_idx, coeff in enumerate(coeffs):
                            if coeff and coeff.strip() and not self._is_valid_number(coeff.strip()):
                                row_issues.append(f"Phương trình {eq_idx+1}, hệ số {coeff_idx+1}: '{coeff}' không phải số hợp lệ")
            except Exception as e:
                row_issues.append(f"Lỗi đọc dữ liệu: {str(e)}")
            
            if has_data:
                quality_info['rows_with_data'] += 1
            
            if row_issues:
                quality_info['rows_with_errors'] += 1
                if len(quality_info['data_issues']) < 10:  # Limit to first 10 errors
                    quality_info['data_issues'].append({
                        'row': row_index + 2,  # Excel row number (1-indexed + header)
                        'issues': row_issues[:3]  # Limit to first 3 issues per row
                    })
        
        return quality_info
    
    def _is_valid_number(self, value: str) -> bool:
        """Check if value is a valid number"""
        try:
            float(value)
            return True
        except:
            return False