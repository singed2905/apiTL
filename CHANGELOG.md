# Changelog

All notable changes to this project will be documented in this file.

## [1.6.0] - 2025-11-11

### 📦 Architecture Improvements (Step 2)
- **Separation of Concerns**
  - Created `geometry_service.py` - dedicated service layer for business logic
  - Refactored `geometry_blueprint.py` to only handle HTTP routing
  - Clear separation: Routes → Service → Config
  
- **Code Organization**
  - Business logic moved from API layer to service layer
  - `geometry_blueprint.py`: ~280 lines (routes only)
  - `geometry_service.py`: ~480 lines (business logic)
  - Better testability - can unit test service without HTTP layer

- **Enhanced Documentation**
  - Added comprehensive docstrings to all service methods
  - Documented input/output formats
  - Improved code readability and maintainability

### 🔧 Technical Improvements
- Service layer pattern implementation
- Cleaner dependency injection
- Easier to mock for testing
- Foundation for future enhancements (e.g., caching, logging)

### 📝 Benefits
- **Maintainability**: Logic changes don't affect route definitions
- **Testability**: Service methods can be tested independently
- **Scalability**: Easy to add new features without touching routes
- **Consistency**: Same pattern can be applied to equation and polynomial APIs

---

## [1.5.0] - 2025-11-11

### 🎯 Major Refactoring (Step 1)
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

---

## Refactoring Roadmap

### ✅ Completed
- [x] Step 1: Convert Geometry to Blueprint pattern (v1.5.0)
- [x] Step 2: Separate business logic into service layer (v1.6.0)

### 🚧 Planned
- [ ] Step 3: Extract encoding logic to `core/encoders.py`
- [ ] Step 4: Add Pydantic models for validation
- [ ] Step 5: Implement unit tests
- [ ] Step 6: Add OpenAPI/Swagger documentation
- [ ] Step 7: Apply same refactoring to Equation and Polynomial APIs
