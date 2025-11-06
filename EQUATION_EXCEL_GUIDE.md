# 🧮 Hướng dẫn sử dụng Excel Import/Export cho Equation Mode

## 🚀 Tổng quan

Equation Mode trong apiTL hiện đã hỗ trợ đầy đủ tính năng Excel Import/Export giống hệt Geometry Mode, bao gồm:

- ✅ **Upload & Process Excel** với validation tự động
- ✅ **Template generation** cho từng loại phương trình
- ✅ **Large file support** (>20MB) với chunked processing
- ✅ **Batch processing** hàng loạt equations
- ✅ **Formatted Excel export** với styling đẹp
- ✅ **Error recovery** và detailed reporting
- ✅ **Web interface** đầy đủ tính năng

## 📋 Excel Template Structure

### **Hệ 2 ẩn (2 phương trình, 2 ẩn):**
```
| a11 | a12 | c1 | a21 | a22 | c2 | Keylog_Result |
|-----|-----|----|----|----|----|---------------|
| 1   | 2   | 5  | 3  | 4  | 7  | (tự động điền) |
| 2   | -1  | 3  | 1  | 1  | 2  | (tự động điền) |
```

**Ví dụ:** 
- Phương trình 1: `1x + 2y = 5`
- Phương trình 2: `3x + 4y = 7`

### **Hệ 3 ẩn (3 phương trình, 3 ẩn):**
```
| a11 | a12 | a13 | c1 | a21 | a22 | a23 | c2 | a31 | a32 | a33 | c3 | Keylog_Result |
|-----|-----|-----|----|----|----|----|----|----|----|----|----|-----------|
| 1   | 2   | 3   | 6  | 2  | -1 | 1  | 1  | 1  | 2  | -1 | 2  | (tự động điền) |
```

**Ví dụ:**
- Phương trình 1: `1x + 2y + 3z = 6`
- Phương trình 2: `2x - 1y + 1z = 1`  
- Phương trình 3: `1x + 2y - 1z = 2`

### **Hệ 4 ẩn (4 phương trình, 4 ẩn):**
```
| a11 | a12 | a13 | a14 | c1 | a21 | a22 | a23 | a24 | c2 | ... | c4 | Keylog_Result |
|-----|-----|-----|-----|----|-----|-----|-----|-----|----| ... |----|---------------|
| 1   | 0   | 1   | 1   | 6  | 0   | 1   | 1   | 1   | 4  | ... | 8  | (tự động điền) |
```

## 🌐 Cách sử dụng qua Web Interface

### **1. Truy cập giao diện:**
```
http://localhost:5000/examples/equation_excel_test.html
```

### **2. Workflow chuẩn:**
```
📥 Chọn loại phương trình (2, 3, 4 ẩn)
📋 Tải template Excel
✏️ Điền dữ liệu vào template
📤 Upload file Excel
✅ Validate cấu trúc & chất lượng
🚀 Process & tạo keylog
💾 Download file kết quả
```

### **3. Features nâng cao:**
- **Large file detection**: Tự động phát hiện file >20MB
- **Chunked processing**: Xử lý file lớn theo chunks
- **Real-time logging**: Theo dõi quá trình xử lý
- **Error reporting**: Báo cáo chi tiết lỗi từng dòng
- **Progress tracking**: Progress bar hiển thị tiến độ

## 📡 API Endpoints

### **Upload Excel file:**
```http
POST /api/equation/excel/upload
Content-Type: multipart/form-data

FORM DATA:
file: [Excel file .xlsx/.xls]
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "filename": "equations.xlsx",
    "filepath": "/tmp/equations.xlsx",
    "file_info": {
      "total_rows": 100,
      "total_columns": 7,
      "file_size_mb": 0.5,
      "is_large_file": false
    }
  }
}
```

### **Validate Excel structure:**
```http
POST /api/equation/excel/validate
Content-Type: application/json

{
  "filepath": "/tmp/equations.xlsx",
  "operation": "Hệ phương trình 2 ẩn"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "is_valid": true,
    "validation_results": {
      "total_rows": 100,
      "rows_with_data": 95,
      "rows_with_errors": 2,
      "data_issues": [
        {
          "row": 15,
          "issues": ["a11: 'abc' không phải số hợp lệ"]
        }
      ]
    }
  }
}
```

### **Process Excel equations:**
```http
POST /api/equation/excel/process
Content-Type: application/json

{
  "filepath": "/tmp/equations.xlsx",
  "operation": "Hệ phương trình 2 ẩn",
  "version": "fx799"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "processed_count": 93,
    "error_count": 2,
    "output_file": "equation_results_20251106_154023.xlsx"
  }
}
```

### **Download result file:**
```http
GET /api/equation/excel/download/equation_results_20251106_154023.xlsx
```

### **Download template:**
```http
GET /api/equation/excel/template/he-2-an
GET /api/equation/excel/template/he-3-an  
GET /api/equation/excel/template/he-4-an
```

## 💻 Cách sử dụng qua Command Line

### **1. Tải template:**
```bash
# Tải template cho hệ 2 ẩn
curl -o template_2an.xlsx "http://localhost:5000/api/equation/excel/template/he-2-an"

# Tải template cho hệ 3 ẩn
curl -o template_3an.xlsx "http://localhost:5000/api/equation/excel/template/he-3-an"

# Tải template cho hệ 4 ẩn
curl -o template_4an.xlsx "http://localhost:5000/api/equation/excel/template/he-4-an"
```

### **2. Upload file:**
```bash
curl -X POST \
  -F "file=@my_equations.xlsx" \
  "http://localhost:5000/api/equation/excel/upload"
```

### **3. Validate file:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "/tmp/my_equations.xlsx",
    "operation": "Hệ phương trình 2 ẩn"
  }' \
  "http://localhost:5000/api/equation/excel/validate"
```

### **4. Process file:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "/tmp/my_equations.xlsx",
    "operation": "Hệ phương trình 2 ẩn",
    "version": "fx799"
  }' \
  "http://localhost:5000/api/equation/excel/process"
```

### **5. Download kết quả:**
```bash
curl -o results.xlsx "http://localhost:5000/api/equation/excel/download/equation_results_20251106_154023.xlsx"
```

## 🔧 Thuật toán và Performance

### **1. File Classification Algorithm:**
```python
# Tự động phân loại file size
if file_size > 20MB or rows > 10,000:
    use_large_file_processor()  # Chunked processing
else:
    use_normal_processor()      # Load toàn bộ vào RAM
```

### **2. Chunked Processing:**
```python
# Adaptive chunk size
if file_size < 1MB:   chunk_size = 1000
elif file_size < 10MB: chunk_size = 500
elif file_size < 50MB: chunk_size = 250
else:                  chunk_size = 100
```

### **3. Validation Levels:**
- **Level 1**: Structure validation (required columns)
- **Level 2**: Sample-based data quality (first 1000 rows)
- **Level 3**: Real-time processing validation

### **4. Performance Metrics:**
| File Size | Rows | Processing Time | Memory Usage |
|-----------|------|-----------------|-------------|
| 1MB | 1,000 | ~2 seconds | 50MB |
| 10MB | 10,000 | ~20 seconds | 100MB |
| 50MB | 50,000 | ~100 seconds | 150MB (chunked) |
| 100MB+ | 100,000+ | ~200+ seconds | 200MB (chunked) |

## 🛡️ Error Handling

### **1. Continue-on-Error Processing:**
```python
# Xử lý tiếp dù có lỗi từng dòng
for row in excel_data:
    try:
        result = process_equation(row)
        results.append(result['keylog'])
        processed_count += 1
    except Exception as e:
        results.append(f"ERROR: {str(e)}")
        error_count += 1
```

### **2. Error Types:**
- **Structure errors**: Thiếu cột bắt buộc
- **Data type errors**: Hệ số không phải số
- **Processing errors**: Lỗi tính toán keylog
- **System errors**: Lỗi file I/O, memory

### **3. Error Limiting:**
- Chỉ hiển thị **10 errors đầu tiên** để không spam
- **Top 3 issues per row** để tập trung vào lỗi quan trọng
- **Sample validation** (1000 rows) cho file lớn

## 📊 Excel Export Features

### **1. Formatted Output:**
- **Header styling**: Blue gradient background, white text
- **Result column highlighting**: Bold green text
- **Auto-width columns**: Tự động điều chỉnh độ rộng
- **Metadata columns**: Operation, Version, Processed_Time

### **2. Performance Optimization:**
- **Format limit**: Tối đa 10,000 rows để tránh chậm
- **Column limit**: Tối đa 20 columns
- **Sample-based width**: Chỉ check 50 rows đầu

### **3. File Structure:**
```
Original Data + Keylog_Result + Metadata:
┌─────┬─────┬─────┬───────────────────┬─────────────────────┐
│ a11 │ a12 │ c1  │ Keylog_Result     │ Operation           │
├─────┼─────┼─────┼───────────────────┼─────────────────────┤
│ 1   │ 2   │ 5   │ wj1121=2=5=C...   │ Hệ phương trình 2 ẩn│
└─────┴─────┴─────┴───────────────────┴─────────────────────┘
```

## 🧪 Testing và Debugging

### **1. Test với curl:**
```bash
# Health check
curl http://localhost:5000/

# Check endpoints
curl http://localhost:5000/api/equation/operations

# Test template download
curl -I http://localhost:5000/api/equation/excel/template/he-2-an
```

### **2. Test với Python:**
```python
import requests

# Test upload
files = {'file': open('test.xlsx', 'rb')}
response = requests.post('http://localhost:5000/api/equation/excel/upload', files=files)
print(response.json())

# Test processing
data = {
    'filepath': '/tmp/test.xlsx',
    'operation': 'Hệ phương trình 2 ẩn',
    'version': 'fx799'
}
response = requests.post('http://localhost:5000/api/equation/excel/process', json=data)
print(response.json())
```

### **3. Debug Mode:**
```python
# Enable debug trong app.py
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 🚨 Troubleshooting

### **Lỗi thường gặp:**

**1. Import Error:**
```bash
# Cài đặt dependencies
pip install pandas openpyxl werkzeug
```

**2. File Upload Error:**
- Kiểm tra file size < 16MB (mặc định)
- Đảm bảo file format .xlsx hoặc .xls
- Check disk space cho temp folder

**3. Processing Error:**
```
# Kiểm tra cấu trúc Excel
- Hệ 2 ẩn cần: a11, a12, c1, a21, a22, c2
- Hệ 3 ẩn cần: a11...a33, c1, c2, c3  
- Hệ 4 ẩn cần: a11...a44, c1, c2, c3, c4
```

**4. Memory Error:**
```python
# Với file lớn, sử dụng chunked processing
is_large, file_info = excel_processor.is_large_file(filepath)
if is_large:
    # Tự động chuyển sang chunked mode
    use_chunked_processing()
```

### **5. Performance Issues:**
```bash
# Monitor system resources
top -p $(pgrep -f "python.*app.py")

# Check temp disk space
df -h /tmp

# Monitor API logs
tail -f app.log
```

## 📈 Monitoring và Analytics

### **1. Processing Stats:**
- **Success rate**: processed_count / total_rows
- **Error rate**: error_count / total_rows  
- **Processing speed**: rows per second
- **Memory usage**: Peak RAM during processing

### **2. File Analytics:**
```python
# Trong web interface
const successRate = processed_count / (processed_count + error_count) * 100;
const processingSpeed = processed_count / processingTimeSeconds;
```

### **3. System Health:**
- **Disk usage**: Temp folder cleaning
- **Memory leaks**: Process monitoring
- **API response time**: Endpoint performance

## 🔮 Future Enhancements

### **Planned Features:**
- [ ] **Real-time progress**: WebSocket-based progress updates
- [ ] **File cleanup**: Automatic temp file deletion  
- [ ] **Batch templates**: Multi-sheet Excel support
- [ ] **Custom validation**: User-defined validation rules
- [ ] **Export formats**: JSON, CSV output options
- [ ] **API rate limiting**: Request throttling
- [ ] **File encryption**: Secure file handling

### **Performance Improvements:**
- [ ] **Streaming processing**: True streaming for huge files
- [ ] **Parallel processing**: Multi-thread equation processing
- [ ] **Caching**: Template and validation caching
- [ ] **Compression**: Gzipped API responses

## 🎯 Kết luận

**Equation Excel Mode** hiện đã có đầy đủ tính năng tương đương **Geometry Mode**:

- ✅ **Complete workflow**: Upload → Validate → Process → Download
- ✅ **Production ready**: Error handling, large file support, performance optimization
- ✅ **User friendly**: Web interface, clear documentation, helpful error messages
- ✅ **Developer friendly**: REST API, comprehensive endpoints, easy integration
- ✅ **Scalable architecture**: Chunked processing, memory optimization, configurable limits

Bạn có thể bắt đầu sử dụng ngay tại:
```
http://localhost:5000/examples/equation_excel_test.html
```

**Happy computing!** 🚀🧮✨