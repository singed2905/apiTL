# Changelog

All notable changes to this project will be documented in this file.

## [1.5.0] - 2025-11-11

### 🎯 Major Refactoring
- **Geometry API refactored to Blueprint pattern**
  - Created `geometry_blueprint.py` separating routes from `app.py`
  - Consistent structure with `equation_api` and `polynomial_api`
  - Better code organization and maintainability
  - Reduced `app.py` from 250+ lines to ~160 lines

### ✨ New Features
- **Geometry Validation Endpoint**
  - `POST /api/geometry/validate` - Validate input data before processing
  - Returns detailed errors and warnings
  - Helps catch issues early in the request pipeline

- **Geometry Template Endpoints**
  - `GET /api/geometry/template/<shape>` - Get input template for single shape
  - `GET /api/geometry/template/<shape_a>/<shape_b>` - Get template for shape pairs
  - Includes examples, field descriptions, and usage notes
  - Supports all 5 geometry types: Điểm, Đường thẳng, Mặt phẳng, Đường tròn, Mặt cầu

### 🔧 Improvements
- Simplified `app.py` - now only handles blueprint registration and error handlers
- All geometry-related routes moved to dedicated blueprint
- Added comprehensive docstrings to all endpoints
- Improved error messages and HTTP status codes
- Better separation of concerns between API and business logic
- Enhanced health check endpoint with changelog information

### 📝 Documentation
- Added CHANGELOG.md for version tracking
- Updated inline code documentation
- Improved API endpoint descriptions

### 🔄 Breaking Changes
None - All endpoints remain backward compatible

---

## [1.4.0] - 2024-11-04

### Features
- Excel Import/Export for Equation Mode
  - Upload Excel files with equation data
  - Process batch calculations from Excel
  - Download results as Excel files
  - Template generation for different equation types
- Polynomial Mode (PT bậc 2, 3, 4)
  - Solve polynomial equations
  - Support for complex roots
  - LaTeX coefficient encoding
  - Batch processing

---

## [1.3.0] - 2024-10-15

### Features
- Geometry Mode
  - 5 geometric shapes: Point, Line, Plane, Circle, Sphere
  - 5 operations: Intersection, Distance, Area, Volume, Line Equation
  - Support for 2D and 3D calculations
- Equation Mode
  - Systems of equations: 2, 3, and 4 unknowns
  - Matrix coefficient encoding
- LaTeX encoding support
  - sqrt, frac, trigonometric functions
  - Custom encoding rules via JSON config
- Multiple calculator version support
  - fx799, fx800, fx801, fx802, fx803
- Config-driven architecture
  - JSON-based configuration files
  - Easy to extend and customize

---

## [1.0.0] - Initial Release

### Features
- Basic Flask API structure
- CORS support
- Static file serving for examples
- Error handling
