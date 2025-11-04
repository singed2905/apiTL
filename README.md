# ConvertKeylogApp Geometry API

🧮 **REST API cho chức năng hình học từ ConvertKeylogApp** - Chuyển đổi các bài toán hình học thành keylog tương thích với máy tính Casio.

## Tổng quan

API này cung cấp các endpoint RESTful để xử lý các phép tính hình học và tạo keylog cho máy tính Casio, được chuyển đổi từ chức năng Geometry Mode của ConvertKeylogApp desktop.

### Tính năng chính

- ✅ **5 hình học cơ bản**: Điểm, Đường thẳng, Mặt phẳng, Đường tròn, Mặt cầu
- ✅ **5 phép toán**: Tương giao, Khoảng cách, Diện tích, Thể tích, PT đường thẳng
- ✅ **Hỗ trợ đa phiên bản máy tính**: fx799, fx800, fx801, fx802, fx803
- ✅ **LaTeX encoding**: Chuyển đổi biểu thức toán học sang keylog
- ✅ **Batch processing**: Xử lý nhiều tính toán cùng lúc
- ✅ **Input validation**: Kiểm tra dữ liệu đầu vào
- ✅ **CORS enabled**: Hỗ trợ tích hợp web frontend

## Cài đặt và chạy

### 1. Clone repository
```bash
git clone https://github.com/singed2905/apiTL.git
cd apiTL
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Chạy API
```bash
python app.py
```

API sẽ chạy tại: `http://localhost:5000`

### 4. Kiểm tra API
```bash
curl http://localhost:5000
```

## API Endpoints

### 🏠 Health Check
```
GET /
```
Kiểm tra trạng thái API và xem danh sách endpoints có sẵn.

### 📐 Geometry Operations

#### Lấy danh sách hình học
```
GET /api/geometry/shapes
```
**Response:**
```json
{
  "status": "success",
  "data": ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]
}
```

#### Lấy danh sách phép toán
```
GET /api/geometry/operations
```
**Response:**
```json
{
  "status": "success",
  "data": ["Tương giao", "Khoảng cách", "Diện tích", "Thể tích", "PT đường thẳng"]
}
```

#### Lấy hình học phù hợp cho phép toán
```
GET /api/geometry/operations/{operation}/shapes
```
**Ví dụ:**
```
GET /api/geometry/operations/Khoảng cách/shapes
```

### 🔢 Processing

#### Xử lý tính toán đơn lẻ
```
POST /api/geometry/process
```

**Request Body:**
```json
{
  "operation": "Khoảng cách",
  "shape_A": "Điểm", 
  "data_A": {
    "point_input": "1,2,3"
  },
  "shape_B": "Điểm",
  "data_B": {
    "point_input": "4,5,6"
  },
  "dimension_A": "3",
  "dimension_B": "3",
  "version": "fx799"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "operation": "Khoảng cách",
    "shape_A": "Điểm",
    "shape_B": "Điểm", 
    "keylog": "wj1131=2=3=CqT11T1224=5=6=CqT3T1RT2=",
    "encoded_A": ["1", "2", "3"],
    "encoded_B": ["4", "5", "6"],
    "timestamp": "2024-11-04T09:00:00"
  }
}
```

#### Xử lý batch
```
POST /api/geometry/batch
```

**Request Body:**
```json
{
  "calculations": [
    {
      "operation": "Diện tích",
      "shape_A": "Đường tròn",
      "data_A": {
        "circle_center": "0,0",
        "circle_radius": "5"
      },
      "version": "fx799"
    },
    {
      "operation": "Thể tích", 
      "shape_A": "Mặt cầu",
      "data_A": {
        "sphere_center": "0,0,0",
        "sphere_radius": "3"
      }
    }
  ]
}
```

### 📝 Templates và Validation

#### Lấy template đầu vào
```
GET /api/geometry/template/{shape_A}
GET /api/geometry/template/{shape_A}/{shape_B}
```

#### Validate dữ liệu đầu vào
```
POST /api/geometry/validate
```

## Ví dụ sử dụng

### JavaScript/Web Integration

```javascript
// Tính khoảng cách giữa 2 điểm
const response = await fetch('http://localhost:5000/api/geometry/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    operation: 'Khoảng cách',
    shape_A: 'Điểm',
    data_A: { point_input: '1,2,3' },
    shape_B: 'Điểm', 
    data_B: { point_input: '4,5,6' },
    dimension_A: '3',
    dimension_B: '3'
  })
});

const result = await response.json();
console.log('Keylog:', result.data.keylog);
```

### Python Integration

```python
import requests

# Tính diện tích đường tròn
data = {
    "operation": "Diện tích",
    "shape_A": "Đường tròn",
    "data_A": {
        "circle_center": "0,0",
        "circle_radius": "sqrt(5)"
    },
    "version": "fx799"
}

response = requests.post('http://localhost:5000/api/geometry/process', json=data)
result = response.json()

print(f"Keylog: {result['data']['keylog']}")
# Output: wj410=0=s5)=CqT4T1=
```

## Cấu trúc dữ liệu đầu vào

### Điểm
```json
{
  "point_input": "x,y,z"  // 2D: "x,y", 3D: "x,y,z"
}
```

### Đường thẳng
```json
{
  "line_A1": "x0,y0,z0",  // Điểm trên đường thẳng
  "line_X1": "dx,dy,dz"   // Vector chỉ phương
}
```

### Mặt phẳng
```json
{
  "plane_a": "a",  // Hệ số x
  "plane_b": "b",  // Hệ số y  
  "plane_c": "c",  // Hệ số z
  "plane_d": "d"   // Hằng số
}
```

### Đường tròn
```json
{
  "circle_center": "x,y",  // Tâm đường tròn
  "circle_radius": "r"     // Bán kính
}
```

### Mặt cầu
```json
{
  "sphere_center": "x,y,z",  // Tâm mặt cầu
  "sphere_radius": "r"       // Bán kính
}
```

## Hỗ trợ LaTeX

API hỗ trợ chuyển đổi biểu thức LaTeX phổ biến:

- `sqrt{5}` → `s5)`
- `\\frac{1}{2}` → `1a2`
- `sin(x)` → `j(x`
- `cos(x)` → `k(x`
- `ln(x)` → `h(x`
- `-` → `p`

## Error Handling

API trả về các mã lỗi HTTP chuẩn:

- `200`: Success
- `400`: Bad Request (dữ liệu đầu vào không hợp lệ)
- `404`: Not Found (endpoint không tồn tại)
- `500`: Internal Server Error

**Ví dụ error response:**
```json
{
  "status": "error",
  "message": "Missing required field: operation"
}
```

## Production Deployment

### Với Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Với Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Tích hợp với Web Frontend

API được thiết kế để tích hợp dễ dàng với:

- ✅ **React/Vue.js/Angular** - Modern SPA frameworks
- ✅ **jQuery** - Traditional web development
- ✅ **Mobile Apps** - React Native, Flutter
- ✅ **Desktop Apps** - Electron, Tauri

## Phát triển và đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Tạo Pull Request

## License

MIT License - Xem [LICENSE](LICENSE) để biết chi tiết.

## Liên hệ

- **Author**: singed2905
- **Repository**: https://github.com/singed2905/apiTL
- **Original App**: https://github.com/singed2905/ConvertKeylogApp

---

*Được chuyển đổi từ [ConvertKeylogApp](https://github.com/singed2905/ConvertKeylogApp) - Desktop app cho việc chuyển đổi biểu thức toán học sang keylog máy tính Casio.*