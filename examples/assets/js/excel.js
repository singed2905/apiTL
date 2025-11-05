let excelJsonData = [];

// Column mapping from clone format
const COLUMN_ALIASES = {
    plane: { A: ['plane_a', 'P1_a'], B: ['plane_a', 'P2_a'] },
    planeb: { A: ['plane_b', 'P1_b'], B: ['plane_b', 'P2_b'] },
    planec: { A: ['plane_c', 'P1_c'], B: ['plane_c', 'P2_c'] },
    planed: { A: ['plane_d', 'P1_d'], B: ['plane_d', 'P2_d'] },
    line_point: { A: ['line_A1', 'd_P_data_A', 'P1_P'], B: ['line_A2', 'd_P_data_B', 'P2_P'] },
    line_vec: { A: ['line_X1', 'd_V_data_A', 'P1_V'], B: ['line_X2', 'd_V_data_B', 'P2_V'] },
    point: { A: ['point_input', 'data_A', 'P1'], B: ['point_input', 'data_B', 'P2'] },
    circle_center: { A: ['circle_center', 'c_center_A', 'C1_center'], B: ['circle_center', 'c_center_B', 'C2_center'] },
    circle_radius: { A: ['circle_radius', 'c_radius_A', 'C1_radius'], B: ['circle_radius', 'c_radius_B', 'C2_radius'] },
    sphere_center: { A: ['sphere_center', 's_center_A', 'S1_center'], B: ['sphere_center', 's_center_B', 'S2_center'] },
    sphere_radius: { A: ['sphere_radius', 's_radius_A', 'S1_radius'], B: ['sphere_radius', 's_radius_B', 'S2_radius'] }
};

const SHAPE_TEMPLATES = {
    'Điểm': { required: ['point'] },
    'Đường thẳng': { required: ['line_point', 'line_vec'] },
    'Mặt phẳng': { required: ['plane', 'planeb', 'planec', 'planed'] },
    'Đường tròn': { required: ['circle_center', 'circle_radius'] },
    'Mặt cầu': { required: ['sphere_center', 'sphere_radius'] }
};

async function handleExcelLocal() {
    const fileInput = document.getElementById('excelFile');
    const file = fileInput.files[0];
    if (!file) return;
    
    try {
        const jsonData = await readExcelFile(file);
        excelJsonData = jsonData;
        
        document.getElementById('fileInfo').style.display = 'block';
        document.getElementById('processingConfig').style.display = 'block';
        
        populateBatchConfig();
        
        const operation = document.getElementById('operation').value;
        const shapeA = document.getElementById('shapeA').value;
        const shapeB = document.getElementById('shapeB').value;
        
        const validation = validateExcelStructure(jsonData, operation, shapeA, shapeB);
        
        displayValidationResults(validation);
        displayFileDetails(file, jsonData);
        displayPreview(jsonData.slice(0, 5));
        
        document.getElementById('processBatchBtn').disabled = !validation.valid;
    } catch (error) {
        showError('Không đọc được file Excel: ' + error.message);
        console.error('Excel reading error:', error);
    }
}

function readExcelFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: 'array' });
                const worksheet = workbook.Sheets[workbook.SheetNames[0]];
                const jsonData = XLSX.utils.sheet_to_json(worksheet, { defval: '' });
                resolve(jsonData);
            } catch (error) {
                reject(error);
            }
        };
        
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
    });
}

function populateBatchConfig() {
    document.getElementById('batchOperation').innerHTML = document.getElementById('operation').innerHTML;
    document.getElementById('batchShapeA').innerHTML = document.getElementById('shapeA').innerHTML;
    document.getElementById('batchShapeB').innerHTML = document.getElementById('shapeB').innerHTML;
}

function validateExcelStructure(jsonData, operation, shapeA, shapeB) {
    const result = {
        valid: true,
        errors: [],
        suggestions: [],
        detected_columns: []
    };
    
    if (!jsonData || jsonData.length === 0) {
        result.valid = false;
        result.errors.push('File Excel trống hoặc không có dữ liệu');
        return result;
    }
    
    const columns = Object.keys(jsonData[0]);
    result.detected_columns = columns;
    
    const checkShape = (shape, group) => {
        const template = SHAPE_TEMPLATES[shape];
        if (!template) return;
        
        template.required.forEach(token => {
            const aliases = COLUMN_ALIASES[token][group];
            const found = aliases.some(alias => columns.includes(alias));
            
            if (!found) {
                result.valid = false;
                result.errors.push(`${shape} (${group}) thiếu cột tương ứng: ${aliases.join(' | ')}`);
            }
        });
    };
    
    if (shapeA) checkShape(shapeA, 'A');
    if (shapeB && !['Diện tích', 'Thể tích'].includes(operation)) {
        checkShape(shapeB, 'B');
    }
    
    return result;
}

function displayValidationResults(validation) {
    const container = document.getElementById('validationResults');
    
    let html = '<div class="validation-summary">';
    
    if (validation.valid) {
        html += '<div class="validation-success">✅ File Excel hợp lệ theo mapping clone!</div>';
    } else {
        html += '<div class="validation-error">❌ File Excel chưa khớp mapping</div>';
    }
    
    html += `<div class="detected-columns">
        <h5>📋 Các cột được phát hiện:</h5>
        <div class="column-list">${validation.detected_columns.join(', ')}</div>
    </div>`;
    
    if (validation.errors.length > 0) {
        html += '<div class="validation-errors"><h5>🚨 Lỗi:</h5><ul>';
        validation.errors.forEach(error => {
            html += `<li>${error}</li>`;
        });
        html += '</ul></div>';
    }
    
    if (validation.suggestions.length > 0) {
        html += '<div class="validation-suggestions"><h5>💡 Gợi ý:</h5><ul>';
        validation.suggestions.forEach(suggestion => {
            html += `<li>${suggestion}</li>`;
        });
        html += '</ul></div>';
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function displayFileDetails(file, jsonData) {
    const container = document.getElementById('fileDetails');
    const sizeKB = (file.size / 1024).toFixed(2);
    
    container.innerHTML = `
        <p><strong>Tên file:</strong> ${file.name}</p>
        <p><strong>Kích thước:</strong> ${sizeKB} KB</p>
        <p><strong>Tổng số dòng:</strong> ${jsonData.length}</p>
        <p><strong>Số cột:</strong> ${Object.keys(jsonData[0] || {}).length}</p>
    `;
}

function displayPreview(rows) {
    const container = document.getElementById('previewTable');
    
    if (!rows || rows.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    const columns = Object.keys(rows[0]);
    
    let html = '<h5>Preview (5 dòng đầu tiên):</h5><table class="preview-table"><thead><tr>';
    
    columns.forEach(column => {
        html += `<th>${column}</th>`;
    });
    
    html += '</tr></thead><tbody>';
    
    rows.forEach(row => {
        html += '<tr>';
        columns.forEach(column => {
            html += `<td>${row[column] ?? ''}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function getFirstAvailable(row, keys) {
    for (const key of keys) {
        if (row[key] !== undefined && row[key] !== null && row[key] !== '') {
            return row[key];
        }
    }
    return undefined;
}

function extractShapeData(row, shape, group) {
    const data = {};
    
    if (!shape) return data;
    
    if (shape === 'Điểm') {
        const value = getFirstAvailable(row, COLUMN_ALIASES.point[group]);
        if (value !== undefined) data.point_input = String(value);
    } else if (shape === 'Đường thẳng') {
        const point = getFirstAvailable(row, COLUMN_ALIASES.line_point[group]);
        const vector = getFirstAvailable(row, COLUMN_ALIASES.line_vec[group]);
        if (point !== undefined) data[`line_A${group === 'A' ? 1 : 2}`] = String(point);
        if (vector !== undefined) data[`line_X${group === 'A' ? 1 : 2}`] = String(vector);
    } else if (shape === 'Mặt phẳng') {
        const a = getFirstAvailable(row, COLUMN_ALIASES.plane[group]);
        const b = getFirstAvailable(row, COLUMN_ALIASES.planeb[group]);
        const c = getFirstAvailable(row, COLUMN_ALIASES.planec[group]);
        const d = getFirstAvailable(row, COLUMN_ALIASES.planed[group]);
        if (a !== undefined) data.plane_a = String(a);
        if (b !== undefined) data.plane_b = String(b);
        if (c !== undefined) data.plane_c = String(c);
        if (d !== undefined) data.plane_d = String(d);
    } else if (shape === 'Đường tròn') {
        const center = getFirstAvailable(row, COLUMN_ALIASES.circle_center[group]);
        const radius = getFirstAvailable(row, COLUMN_ALIASES.circle_radius[group]);
        if (center !== undefined) data.circle_center = String(center);
        if (radius !== undefined) data.circle_radius = String(radius);
    } else if (shape === 'Mặt cầu') {
        const center = getFirstAvailable(row, COLUMN_ALIASES.sphere_center[group]);
        const radius = getFirstAvailable(row, COLUMN_ALIASES.sphere_radius[group]);
        if (center !== undefined) data.sphere_center = String(center);
        if (radius !== undefined) data.sphere_radius = String(radius);
    }
    
    return data;
}

async function processBatchChunked() {
    const operation = document.getElementById('batchOperation').value;
    const shapeA = document.getElementById('batchShapeA').value;
    const shapeB = document.getElementById('batchShapeB').value;
    
    if (!operation || !shapeA || excelJsonData.length === 0) {
        showError('Thiếu thông tin cần thiết cho batch processing');
        return;
    }
    
    const chunkSizeInput = document.getElementById('chunkSize');
    const CHUNK_SIZE = Math.max(10, Math.min(1000, parseInt(chunkSizeInput.value || '100', 10)));
    
    const totalRows = excelJsonData.length;
    const results = new Array(totalRows).fill(null);
    const errors = [];
    
    document.getElementById('batchProgress').style.display = 'block';
    
    let processedRows = 0;
    
    // Process in chunks
    for (let i = 0; i < totalRows; i += CHUNK_SIZE) {
        const end = Math.min(i + CHUNK_SIZE, totalRows);
        const chunk = excelJsonData.slice(i, end);
        
        const calculations = chunk.map(row => ({
            operation: operation,
            shape_A: shapeA,
            data_A: extractShapeData(row, shapeA, 'A'),
            shape_B: shapeB || undefined,
            data_B: shapeB ? extractShapeData(row, shapeB, 'B') : undefined
        }));
        
        // Retry logic for each chunk
        let attempt = 0;
        const maxAttempts = 3;
        
        while (attempt < maxAttempts) {
            try {
                const response = await fetch(`${API_BASE}/api/geometry/batch`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ calculations: calculations })
                });
                
                const result = await response.json();
                
                // Store results
                for (let j = 0; j < calculations.length; j++) {
                    results[i + j] = result.data ? result.data[j] : null;
                }
                
                break; // Success, exit retry loop
            } catch (error) {
                attempt++;
                if (attempt >= maxAttempts) {
                    errors.push(`Chunk ${i}-${end} failed after ${maxAttempts} attempts: ${error.message}`);
                    // Fill with null for failed chunk
                    for (let j = 0; j < calculations.length; j++) {
                        results[i + j] = null;
                    }
                }
            }
        }
        
        processedRows = end;
        const percent = Math.round((processedRows / totalRows) * 100);
        
        document.getElementById('progressFill').style.width = percent + '%';
        document.getElementById('progressText').textContent = percent + '%';
    }
    
    // Display results
    document.getElementById('batchResults').style.display = 'block';
    
    const successCount = results.filter(r => r && r.keylog).length;
    const errorCount = totalRows - successCount;
    
    document.getElementById('batchSummary').innerHTML = `
        <p><strong>Tổng số dòng:</strong> ${totalRows}</p>
        <p><strong>Xử lý thành công:</strong> ${successCount}</p>
        <p><strong>Lỗi:</strong> ${errorCount}</p>
        ${errors.length > 0 ? `<p><strong>Chunk errors:</strong> ${errors.length}</p>` : ''}
    `;
    
    // Export results to Excel
    exportResultsToExcel({ data: results });
}

function exportResultsToExcel(processedData) {
    try {
        const rows = [];
        
        for (let i = 0; i < excelJsonData.length; i++) {
            const originalRow = excelJsonData[i];
            const result = processedData.data[i];
            
            rows.push({
                ...originalRow,
                keylog: result && result.keylog ? result.keylog : ''
            });
        }
        
        const worksheet = XLSX.utils.json_to_sheet(rows);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Results');
        
        XLSX.writeFile(workbook, 'geometry_results.xlsx');
    } catch (error) {
        console.error('Export error:', error);
        showError('Không thể xuất file Excel: ' + error.message);
    }
}