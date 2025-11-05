// Batch configuration - fully independent from manual inputs
// New: Populate from availableOperations/availableShapes, add Auto-detect, live revalidate

let excelJsonData = [];

const COLUMN_ALIASES = {
  plane: { A: ['plane_a','P1_a'], B: ['plane_a','P2_a'] },
  planeb:{ A: ['plane_b','P1_b'], B: ['plane_b','P2_b'] },
  planec:{ A: ['plane_c','P1_c'], B: ['plane_c','P2_c'] },
  planed:{ A: ['plane_d','P1_d'], B: ['plane_d','P2_d'] },
  line_point:{ A: ['line_A1','d_P_data_A','P1_P'], B: ['line_A2','d_P_data_B','P2_P'] },
  line_vec:{ A: ['line_X1','d_V_data_A','P1_V'], B: ['line_X2','d_V_data_B','P2_V'] },
  point:{ A: ['point_input','data_A','P1'], B: ['point_input','data_B','P2'] },
  circle_center:{ A: ['circle_center','c_center_A','C1_center'], B: ['circle_center','c_center_B','C2_center'] },
  circle_radius:{ A: ['circle_radius','c_radius_A','C1_radius'], B: ['circle_radius','c_radius_B','C2_radius'] },
  sphere_center:{ A: ['sphere_center','s_center_A','S1_center'], B: ['sphere_center','s_center_B','S2_center'] },
  sphere_radius:{ A: ['sphere_radius','s_radius_A','S1_radius'], B: ['sphere_radius','s_radius_B','S2_radius'] },
};

const SHAPE_TEMPLATES = {
  'Điểm': { required: ['point'] },
  'Đường thẳng': { required: ['line_point','line_vec'] },
  'Mặt phẳng': { required: ['plane','planeb','planec','planed'] },
  'Đường tròn': { required: ['circle_center','circle_radius'] },
  'Mặt cầu': { required: ['sphere_center','sphere_radius'] },
};

// Public API from app.js
// - availableOperations
// - availableShapes

function buildBatchDropdowns(){
  const opSel = document.getElementById('batchOperation');
  const aSel = document.getElementById('batchShapeA');
  const bSel = document.getElementById('batchShapeB');

  // Build fresh (no copy from manual inputs)
  opSel.innerHTML = '<option value="">Chọn phép toán...</option>';
  (availableOperations || []).forEach(op=>{
    const o = document.createElement('option'); o.value = op; o.textContent = op; opSel.appendChild(o);
  });

  const shapeOptions = ['(Auto)', ...(availableShapes||[])];
  aSel.innerHTML=''; bSel.innerHTML='';
  shapeOptions.forEach(s=>{
    const o1=document.createElement('option'); o1.value=s; o1.textContent=s; aSel.appendChild(o1);
    const o2=document.createElement('option'); o2.value=s; o2.textContent=s; bSel.appendChild(o2);
  });

  // Default to Auto
  aSel.value='(Auto)';
  bSel.value='(Auto)';
}

function onBatchConfigChanged(){
  // Re-validate if we already loaded excel
  if (excelJsonData && excelJsonData.length>0){
    const v = validateExcelStructure(excelJsonData, document.getElementById('batchOperation').value,
      document.getElementById('batchShapeA').value, document.getElementById('batchShapeB').value);
    displayValidationResults(v);
    document.getElementById('processBatchBtn').disabled=!v.valid;
  }
}

// Auto-detect shapes from columns if '(Auto)' selected
function autoDetectShape(columns, group){
  // Plane detection
  const hasPlane = ['a','b','c','d'].every(k => columns.includes(`${group==='A'?'P1':'P2'}_${k}`) || columns.includes(`plane_${k}`));
  if (hasPlane) return 'Mặt phẳng';

  // Line detection
  const hasLine = (columns.some(c=> c===`line_A${group==='A'?1:2}` || c===`d_P_data_${group}` || c===`${group==='A'?'P1':'P2'}_P`)) &&
                  (columns.some(c=> c===`line_X${group==='A'?1:2}` || c===`d_V_data_${group}` || c===`${group==='A'?'P1':'P2'}_V`));
  if (hasLine) return 'Đường thẳng';

  // Point detection
  const hasPoint = columns.some(c=> c==='point_input' || c=== (group==='A'?'data_A':'data_B') || c=== (group==='A'?'P1':'P2'));
  if (hasPoint) return 'Điểm';

  // Circle detection
  const hasCircle = columns.some(c=> c==='circle_center' || c==='c_center_A' || c==='c_center_B' || c==='C1_center' || c==='C2_center') &&
                    columns.some(c=> c==='circle_radius' || c==='c_radius_A' || c==='c_radius_B' || c==='C1_radius' || c==='C2_radius');
  if (hasCircle) return 'Đường tròn';

  // Sphere detection
  const hasSphere = columns.some(c=> c==='sphere_center' || c==='s_center_A' || c==='s_center_B' || c==='S1_center' || c==='S2_center') &&
                    columns.some(c=> c==='sphere_radius' || c==='s_radius_A' || c==='s_radius_B' || c==='S1_radius' || c==='S2_radius');
  if (hasSphere) return 'Mặt cầu';

  return '';
}

function validateExcelStructure(jsonData, operation, shapeA, shapeB){
  const result = { valid: true, errors: [], suggestions: [], detected_columns: [] };
  if (!jsonData || jsonData.length === 0) { result.valid = false; result.errors.push('File Excel trống hoặc không có dữ liệu'); return result; }
  const columns = Object.keys(jsonData[0]); result.detected_columns = columns;

  // Auto-detect if requested
  const effShapeA = (shapeA === '(Auto)') ? autoDetectShape(columns, 'A') : shapeA;
  const effShapeB = (shapeB === '(Auto)') ? autoDetectShape(columns, 'B') : shapeB;

  const check = (shape, group) => {
    const t = SHAPE_TEMPLATES[shape]; if (!t) return;
    t.required.forEach(token => {
      const aliases = COLUMN_ALIASES[token][group];
      const found = aliases.some(alias => columns.includes(alias));
      if (!found) {
        result.valid = false;
        result.errors.push(`${shape} (${group}) thiếu cột tương ứng: ${aliases.join(' | ')}`);
      }
    });
  };

  if (effShapeA) check(effShapeA, 'A');
  if (effShapeB && !['Diện tích','Thể tích'].includes(operation)) check(effShapeB, 'B');

  // Attach effective shapes info for UI
  result.effective = { shapeA: effShapeA || shapeA, shapeB: effShapeB || shapeB };
  return result;
}

function displayValidationResults(validation){
  const container = document.getElementById('validationResults');
  let html = '<div class="validation-summary">';
  html += validation.valid ? '<div class="validation-success">✅ File Excel hợp lệ theo mapping!</div>' : '<div class="validation-error">❌ File Excel chưa khớp mapping</div>';
  html += `<div class="detected-columns"><h5>📋 Các cột được phát hiện:</h5><div class="column-list">${validation.detected_columns.join(', ')}</div></div>`;
  if (validation.effective){
    html += `<div style="margin-top:8px;font-size:13px;color:#555">Dùng cấu hình: Hình A = <b>${validation.effective.shapeA||'-'}</b>, Hình B = <b>${validation.effective.shapeB||'-'}</b></div>`;
  }
  if (validation.errors.length>0){ html += '<div class="validation-errors"><h5>🚨 Lỗi:</h5><ul>'; validation.errors.forEach(e=> html += `<li>${e}</li>`); html += '</ul></div>'; }
  html += '</div>'; container.innerHTML = html;
}

function populateBatchConfig(){
  // New behavior: build from operations/shapes
  buildBatchDropdowns();
  // Bind change events
  document.getElementById('batchOperation').onchange = onBatchConfigChanged;
  document.getElementById('batchShapeA').onchange = onBatchConfigChanged;
  document.getElementById('batchShapeB').onchange = onBatchConfigChanged;
}

async function handleExcelLocal(){
  const file = document.getElementById('excelFile').files[0];
  if (!file) return;
  try{
    const json = await readExcelFile(file);
    excelJsonData = json;
    document.getElementById('fileInfo').style.display = 'block';
    document.getElementById('processingConfig').style.display = 'block';

    // Ensure batch dropdowns are built and independent
    populateBatchConfig();

    const v = validateExcelStructure(json, document.getElementById('batchOperation').value,
      document.getElementById('batchShapeA').value, document.getElementById('batchShapeB').value);
    displayValidationResults(v);
    displayFileDetails(file, json);
    displayPreview(json.slice(0,5));
    document.getElementById('processBatchBtn').disabled = !v.valid;
  }catch(error){
    showError('Không đọc được file Excel: ' + error.message);
    console.error('Excel reading error:', error);
  }
}

async function processBatchChunked(){
  const operation = document.getElementById('batchOperation').value;
  let shapeA = document.getElementById('batchShapeA').value;
  let shapeB = document.getElementById('batchShapeB').value;
  if (!operation){ showError('Chọn phép toán cho batch'); return; }
  if (!excelJsonData || excelJsonData.length===0){ showError('Chưa có dữ liệu Excel'); return; }

  // Resolve auto shapes based on columns
  const columns = Object.keys(excelJsonData[0]||{});
  if (shapeA==='(Auto)') shapeA = autoDetectShape(columns,'A');
  if (shapeB==='(Auto)') shapeB = autoDetectShape(columns,'B');
  if (!shapeA){ showError('Không nhận diện được Hình A. Vui lòng chọn thủ công.'); return; }
  if (!['Diện tích','Thể tích'].includes(operation) && !shapeB){ showError('Không nhận diện được Hình B. Vui lòng chọn thủ công.'); return; }

  const chunkSize = Math.max(10, Math.min(1000, parseInt(document.getElementById('chunkSize').value||'100',10)));
  const total = excelJsonData.length;
  const results = new Array(total).fill(null);
  const errors = [];
  document.getElementById('batchProgress').style.display='block';

  for(let i=0;i<total;i+=chunkSize){
    const end = Math.min(i+chunkSize, total);
    const calcs = excelJsonData.slice(i,end).map(row=>({
      operation: operation,
      shape_A: shapeA,
      data_A: extractShapeData(row, shapeA, 'A'),
      shape_B: shapeB || undefined,
      data_B: shapeB ? extractShapeData(row, shapeB, 'B') : undefined
    }));
    let attempt=0; while(attempt<3){
      try{
        const response = await fetch(`${API_BASE}/api/geometry/batch`,{ method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ calculations: calcs }) });
        const r = await response.json();
        for(let j=0;j<calcs.length;j++){ results[i+j] = r.data ? r.data[j] : null; }
        break;
      }catch(e){ attempt++; if(attempt>=3){ errors.push(`Chunk ${i}-${end} failed: ${e.message}`); for(let j=0;j<calcs.length;j++){ results[i+j]=null; } } }
    }
    const percent=Math.round(((end)/total)*100); document.getElementById('progressFill').style.width=percent+'%'; document.getElementById('progressText').textContent=percent+'%';
  }

  document.getElementById('batchResults').style.display='block';
  const successCount = results.filter(r=> r && r.keylog).length;
  const errorCount = total - successCount;
  document.getElementById('batchSummary').innerHTML = `
    <p><strong>Tổng số dòng:</strong> ${total}</p>
    <p><strong>Xử lý thành công:</strong> ${successCount}</p>
    <p><strong>Lỗi:</strong> ${errorCount}</p>
    ${errors.length ? `<p><strong>Chunk errors:</strong> ${errors.length}</p>` : ''}
  `;

  exportResultsToExcel({ data: results });
}
