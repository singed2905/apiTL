# ConvertKeylogApp API v2.2.0

🚀 **Spring Boot REST API for ConvertKeylogApp** - Chuyển đổi biểu thức toán học thành keylog máy tính Casio

## 📋 Tổng quan

API này được phát triển dựa trên [ConvertKeylogApp v2.2](https://github.com/singed2905/ConvertKeylogApp) - ứng dụng desktop Python. Cung cấp các RESTful endpoints để chuyển đổi các phép tính toán học phức tạp thành mã keylog tương thích với máy tính Casio.

## 🛠️ Công nghệ sử dụng

- **Java 17** + **Spring Boot 3.2.0**
- **Apache Commons Math3** - Xử lý toán học
- **OpenAPI 3** (Swagger) - API Documentation  
- **Maven** - Build tool
- **Lombok** - Code generation
- **Docker** - Containerization

## 🎯 Chức năng chính

### 🧠 Equation Mode
- Giải hệ phương trình tuyến tính 2×2, 3×3, 4×4
- TL-compatible keylog encoding
- Multi-version calculator support

### 📈 Polynomial Mode  
- Giải phương trình polynomial bậc 2, 3, 4
- Complex roots handling
- 8+ calculator versions với prefix khác nhau

### 📐 Geometry Mode
- 5 hình học cơ bản × 5 phép toán = 25 combinations
- 2D/3D geometry calculations
- LaTeX to calculator encoding

### 🔢 Vector Mode
- Vector operations 2D/3D
- Dot product, cross product, angles

## 🚀 Cách chạy

### Prerequisites
- Java 17+
- Maven 3.6+

### Chạy local
```bash
git clone https://github.com/singed2905/apiTL.git
cd apiTL
mvn spring-boot:run
```

### Chạy với Docker
```bash
docker build -t api-tl:2.2.0 .
docker run -p 8080:8080 api-tl:2.2.0
```

### Chạy với Docker Compose
```bash
docker-compose up -d
```

## 📖 API Documentation

Sau khi chạy ứng dụng:
- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **API Docs**: http://localhost:8080/api-docs
- **Health Check**: http://localhost:8080/actuator/health

## 🔧 API Endpoints

### Equation Mode
```
POST /api/v1/equation/solve      - Giải hệ phương trình
POST /api/v1/equation/keylog     - Tạo keylog 
POST /api/v1/equation/batch      - Batch processing
GET  /api/v1/equation/versions   - Danh sách calculator versions
GET  /api/v1/equation/example/{variables} - Ví dụ hệ phương trình
```

### Polynomial Mode  
```
POST /api/v1/polynomial/solve    - Giải polynomial
POST /api/v1/polynomial/keylog   - Tạo keylog
POST /api/v1/polynomial/batch    - Batch processing
GET  /api/v1/polynomial/versions - Calculator versions
GET  /api/v1/polynomial/prefixes/{version} - Prefix patterns
```

### Geometry & Vector Modes
```
POST /api/v1/geometry/*          - Geometry operations
POST /api/v1/vector/*            - Vector operations
```

## 📝 Request/Response Examples

### Equation Request
```json
{
  "variables": 3,
  "coefficients": ["1", "2", "1", "6", "2", "1", "3", "14", "1", "1", "1", "6"],
  "calculatorVersion": "fx799",
  "problemName": "Hệ 3 ẩn",
  "generateKeylog": true,
  "solveSolution": true
}
```

### Keylog Response
```json
{
  "keylog": "w913=1=2=1=6=2=1=3=14=1=1=1=6== = =",
  "calculatorVersion": "fx799",
  "mode": "EQUATION",
  "prefix": "w913",
  "suffix": "== = =",
  "keylogLength": 45,
  "generatedAt": "2025-11-04T08:10:00",
  "status": "SUCCESS"
}
```

## 🔌 Calculator Support

### Equation Mode (TL-compatible)
| Version | 2 ẩn | 3 ẩn | 4 ẩn |
|---------|------|------|------|
| fx799   | w912 | w913 | w914 |
| fx800-803 | Custom prefixes |

### Polynomial Mode (Multi-version)
| Version | Bậc 2 | Bậc 3 | Bậc 4 | Suffix |
|---------|-------|-------|-------|--------|
| fx799   | P2=   | P3=   | P4=   | ==, ===, ==== |
| fx991   | EQN2= | EQN3= | EQN4= | =0, ==0, ===0 |
| fx570   | POL2= | POL3= | POL4= | =ROOT |
| fx580   | POLY2=| POLY3=| POLY4=| =SOLVE |

## 🏗️ Kiến trúc

```
src/main/java/com/singed2905/apitl/
├── controller/          # REST Controllers
├── service/            # Business Logic
├── model/              # DTOs & Entities
│   ├── request/        # Request models
│   ├── response/       # Response models  
│   └── dto/           # Data transfer objects
├── util/              # Utilities
│   ├── KeylogEncoder  # Keylog encoding logic
│   ├── MathUtils      # Math expression parsing
│   └── CalculatorVersionMapper # Version mappings
└── config/            # Configuration classes
```

## 🧪 Testing

```bash
# Chạy tất cả tests
mvn test

# Chạy integration tests
mvn verify

# Test coverage report
mvn jacoco:report
```

## 🔄 CI/CD

GitHub Actions workflow tự động:
- Build & Test
- Docker image build
- Deploy to staging/production
- API documentation update

## 📊 Monitoring

- **Health checks**: `/actuator/health`
- **Metrics**: `/actuator/metrics`
- **Environment info**: `/actuator/env`
- **Logging**: File-based + Console

## 🚧 Roadmap

### Phase 1 (Hiện tại)
- ✅ Core API endpoints for all 4 modes
- ✅ OpenAPI documentation
- ✅ Docker support
- ✅ Basic error handling

### Phase 2 (Sắp tới)
- 🚧 Database integration (H2/PostgreSQL)
- 🚧 Authentication & Authorization (JWT)
- 🚧 Rate limiting & API throttling
- 🚧 Advanced batch processing with queues

### Phase 3 (Tương lai)
- 🚧 Caching layer (Redis)
- 🚧 WebSocket support for real-time
- 🚧 Multi-language support
- 🚧 Advanced analytics & reporting

## 🤝 Contributing

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

## 📄 License

MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 👨‍💻 Author

**singed2905**
- GitHub: [@singed2905](https://github.com/singed2905)
- Original Project: [ConvertKeylogApp](https://github.com/singed2905/ConvertKeylogApp)

---

**Phiên bản**: 2.2.0  
**Cập nhật lần cuối**: November 4, 2025