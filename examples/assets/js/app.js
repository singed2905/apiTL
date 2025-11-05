const API_BASE = 'http://localhost:5000';
let availableShapes = [];
let availableOperations = [];

async function initApp() {
    try {
        const [shapesRes, operationsRes] = await Promise.all([
            fetch(`${API_BASE}/api/geometry/shapes`),
            fetch(`${API_BASE}/api/geometry/operations`)
        ]);
        
        const shapesData = await shapesRes.json();
        const operationsData = await operationsRes.json();
        
        availableShapes = shapesData.data || [];
        availableOperations = operationsData.data || [];
        
        populateOperations();
        populateShapes();
        setupVisualizationListeners();
        
        // Initialize empty plot
        initializeVisualization();
    } catch (error) {
        showError('Không thể kết nối đến API.');
        console.error('Init error:', error);
    }
}

function populateOperations() {
    const select = document.getElementById('operation');
    select.innerHTML = '<option value="">Chọn phép toán...</option>';
    availableOperations.forEach(op => {
        const option = document.createElement('option');
        option.value = op;
        option.textContent = op;
        select.appendChild(option);
    });
}

function populateShapes() {
    const selectA = document.getElementById('shapeA');
    const selectB = document.getElementById('shapeB');
    selectA.innerHTML = '<option value="">Chọn hình A...</option>';
    selectB.innerHTML = '<option value="">Không có</option>';
    
    availableShapes.forEach(shape => {
        const optionA = document.createElement('option');
        optionA.value = shape;
        optionA.textContent = shape;
        selectA.appendChild(optionA);
        
        const optionB = document.createElement('option');
        optionB.value = shape;
        optionB.textContent = shape;
        selectB.appendChild(optionB);
    });
}

async function updateShapeOptions() {
    const operation = document.getElementById('operation').value;
    if (!operation) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/geometry/operations/${encodeURIComponent(operation)}/shapes`);
        const data = await response.json();
        
        const selectA = document.getElementById('shapeA');
        const selectB = document.getElementById('shapeB');
        
        selectA.innerHTML = '<option value="">Chọn hình A...</option>';
        (data.data || []).forEach(shape => {
            const option = document.createElement('option');
            option.value = shape;
            option.textContent = shape;
            selectA.appendChild(option);
        });
        
        selectB.innerHTML = '<option value="">Không có</option>';
        if (!['Diện tích', 'Thể tích'].includes(operation)) {
            (data.data || []).forEach(shape => {
                const option = document.createElement('option');
                option.value = shape;
                option.textContent = shape;
                selectB.appendChild(option);
            });
        }
        
        updateInputFields();
    } catch (error) {
        console.error('Error updating shapes:', error);
    }
}

function updateInputFields() {
    const shapeA = document.getElementById('shapeA').value;
    const shapeB = document.getElementById('shapeB').value;
    updateShapeInputs('A', shapeA);
    updateShapeInputs('B', shapeB);
    
    // Update visualization when shapes change
    setTimeout(updateVisualization, 100);
}

function updateShapeInputs(group, shape) {
    const container = document.getElementById(`inputs${group}`);
    container.innerHTML = '';
    
    if (!shape) {
        container.classList.remove('active');
        return;
    }
    
    container.classList.add('active');
    
    if (shape === 'Điểm') {
        container.innerHTML = `
            <label>Tọa độ (x,y,z):</label>
            <input type="text" id="point_input_${group}" placeholder="1,2,3" oninput="updateVisualization()">
        `;
    } else if (shape === 'Đường thẳng') {
        container.innerHTML = `
            <label>Điểm trên đường thẳng (x,y,z):</label>
            <input type="text" id="line_A${group === 'A' ? '1' : '2'}_${group}" placeholder="0,0,0" oninput="updateVisualization()">
            <label style="margin-top:10px;">Vector chỉ phương (dx,dy,dz):</label>
            <input type="text" id="line_X${group === 'A' ? '1' : '2'}_${group}" placeholder="1,1,1" oninput="updateVisualization()">
        `;
    } else if (shape === 'Mặt phẳng') {
        container.innerHTML = `
            <label>a, b, c, d:</label>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
                <input id="plane_a_${group}" placeholder="a" oninput="updateVisualization()">
                <input id="plane_b_${group}" placeholder="b" oninput="updateVisualization()">
                <input id="plane_c_${group}" placeholder="c" oninput="updateVisualization()">
                <input id="plane_d_${group}" placeholder="d" oninput="updateVisualization()">
            </div>
        `;
    } else if (shape === 'Đường tròn') {
        container.innerHTML = `
            <label>Tâm (x,y):</label>
            <input id="circle_center_${group}" placeholder="0,0" oninput="updateVisualization()">
            <label style="margin-top:10px;">Bán kính:</label>
            <input id="circle_radius_${group}" placeholder="5" oninput="updateVisualization()">
        `;
    } else if (shape === 'Mặt cầu') {
        container.innerHTML = `
            <label>Tâm (x,y,z):</label>
            <input id="sphere_center_${group}" placeholder="0,0,0" oninput="updateVisualization()">
            <label style="margin-top:10px;">Bán kính:</label>
            <input id="sphere_radius_${group}" placeholder="3" oninput="updateVisualization()">
        `;
    }
}

function collectInputData(group, shape) {
    const data = {};
    
    if (shape === 'Điểm') {
        const input = document.getElementById(`point_input_${group}`);
        if (input) data.point_input = input.value;
    } else if (shape === 'Đường thẳng') {
        const lineA = document.getElementById(`line_A${group === 'A' ? '1' : '2'}_${group}`);
        const lineX = document.getElementById(`line_X${group === 'A' ? '1' : '2'}_${group}`);
        if (lineA) data[`line_A${group === 'A' ? '1' : '2'}`] = lineA.value;
        if (lineX) data[`line_X${group === 'A' ? '1' : '2'}`] = lineX.value;
    } else if (shape === 'Mặt phẳng') {
        ['a', 'b', 'c', 'd'].forEach(coeff => {
            const input = document.getElementById(`plane_${coeff}_${group}`);
            if (input) data[`plane_${coeff}`] = input.value;
        });
    } else if (shape === 'Đường tròn') {
        const center = document.getElementById(`circle_center_${group}`);
        const radius = document.getElementById(`circle_radius_${group}`);
        if (center) data.circle_center = center.value;
        if (radius) data.circle_radius = radius.value;
    } else if (shape === 'Mặt cầu') {
        const center = document.getElementById(`sphere_center_${group}`);
        const radius = document.getElementById(`sphere_radius_${group}`);
        if (center) data.sphere_center = center.value;
        if (radius) data.sphere_radius = radius.value;
    }
    
    return data;
}

async function processGeometry() {
    const operation = document.getElementById('operation').value;
    const shapeA = document.getElementById('shapeA').value;
    const shapeB = document.getElementById('shapeB').value;
    const version = document.getElementById('version').value;
    
    if (!operation || !shapeA) {
        showError('Vui lòng chọn phép toán và hình A.');
        return;
    }
    
    const dataA = collectInputData('A', shapeA);
    const dataB = shapeB ? collectInputData('B', shapeB) : {};
    
    const requestData = {
        operation,
        shape_A: shapeA,
        data_A: dataA,
        version
    };
    
    if (shapeB) {
        requestData.shape_B = shapeB;
        requestData.data_B = dataB;
    }
    
    document.getElementById('results').innerHTML = '<div class="loading">🔄 Đang xử lý...</div>';
    document.getElementById('processBtn').disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/api/geometry/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            displayResults(result.data);
        } else {
            showError(result.message || 'Xử lý thất bại');
        }
    } catch (error) {
        showError('Lỗi kết nối đến API: ' + error.message);
        console.error('Processing error:', error);
    } finally {
        document.getElementById('processBtn').disabled = false;
    }
}

function displayResults(data) {
    const resultsContainer = document.getElementById('results');
    const keylogHtml = `
        <div class="result-item">
            <h4>🔑 Keylog (${data.version}):</h4>
            <div class="keylog">
                ${data.keylog}
                <button class="copy-btn" onclick="copyToClipboard('${data.keylog}')">Copy</button>
            </div>
        </div>
        <div class="result-item">
            <h4>📝 Thông tin:</h4>
            <p><strong>Phép toán:</strong> ${data.operation}</p>
            <p><strong>Hình A:</strong> ${data.shape_A}</p>
            ${data.shape_B ? `<p><strong>Hình B:</strong> ${data.shape_B}</p>` : ''}
            <p><strong>Mã hóa A:</strong> [${(data.encoded_A || []).join(', ')}]</p>
            ${(data.encoded_B && data.encoded_B.length > 0) ? `<p><strong>Mã hóa B:</strong> [${data.encoded_B.join(', ')}]</p>` : ''}
        </div>
        <div class="success">✅ Xử lý thành công! Sao chép keylog và nhập vào máy tính Casio.</div>
    `;
    resultsContainer.innerHTML = keylogHtml;
}

function showError(message) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = `<div class="error">❌ ${message}</div>`;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        btn.style.background = '#27ae60';
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '#3498db';
        }, 1500);
    }).catch(err => {
        console.error('Copy failed:', err);
        alert('Không thể copy. Vui lòng copy thủ công.');
    });
}