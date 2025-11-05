// Excel batch processing with chunking support (restored to 1cb1827-compatible API)
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

async function handleExcelLocal(){
  const f = document.getElementById('excelFile').files[0];
  if(!f) return;
  const json = await readExcelFile(f);
  excelJsonData = json;
  document.getElementById('fileInfo').style.display='block';
  document.getElementById('processingConfig').style.display='block';
  populateBatchConfig();
  const op=document.getElementById('operation').value;
  const sA=document.getElementById('shapeA').value;
  const sB=document.getElementById('shapeB').value;
  const v = validateExcelStructure(json, op, sA, sB);
  displayValidationResults(v);
  displayFileDetails(f, json);
  displayPreview(json.slice(0,5));
  document.getElementById('processBatchBtn').disabled=!v.valid;
}

function readExcelFile(file){
  return new Promise((resolve,reject)=>{
    const reader=new FileReader();
    reader.onload=e=>{
      try{
        const data=new Uint8Array(e.target.result);
        const wb=XLSX.read(data,{type:'array'});
        const ws=wb.Sheets[wb.SheetNames[0]];
        const json=XLSX.utils.sheet_to_json(ws,{defval:''});
        resolve(json);
      }catch(err){ reject(err); }
    };
    reader.onerror=reject;
    reader.readAsArrayBuffer(file);
  });
}

function populateBatchConfig(){
  document.getElementById('batchOperation').innerHTML=document.getElementById('operation').innerHTML;
  document.getElementById('batchShapeA').innerHTML=document.getElementById('shapeA').innerHTML;
  document.getElementById('batchShapeB').innerHTML=document.getElementById('shapeB').innerHTML;
}

function validateExcelStructure(json, op, sA, sB){
  const out={valid:true, errors:[], detected_columns:[]};
  if(!json||json.length===0){ out.valid=false; out.errors.push('File Excel trống'); return out; }
  const cols=Object.keys(json[0]); out.detected_columns=cols;
  const check=(shape, group)=>{
    const t=SHAPE_TEMPLATES[shape]; if(!t) return;
    t.required.forEach(token=>{
      const aliases=COLUMN_ALIASES[token][group];
      const found=aliases.some(k=> cols.includes(k));
      if(!found) out.valid=false, out.errors.push(`${shape} (${group}) thiếu cột: ${aliases.join(' | ')}`);
    });
  };
  if(sA) check(sA,'A');
  if(sB && !['Diện tích','Thể tích'].includes(op)) check(sB,'B');
  return out;
}

function displayValidationResults(v){
  const c=document.getElementById('validationResults');
  let h='<div class="validation-summary">';
  h+= v.valid?'<div class="validation-success">✅ File Excel hợp lệ theo mapping clone!</div>':'<div class="validation-error">❌ File Excel chưa khớp mapping</div>';
  h+=`<div class="detected-columns"><h5>📋 Các cột:</h5><div class="column-list">${v.detected_columns.join(', ')}</div></div>`;
  if(v.errors.length>0){ h+='<div class="validation-errors"><h5>🚨 Lỗi:</h5><ul>'; v.errors.forEach(e=> h+=`<li>${e}</li>` ); h+='</ul></div>'; }
  h+='</div>'; c.innerHTML=h;
}

function displayFileDetails(file, json){
  const c=document.getElementById('fileDetails');
  c.innerHTML = `<p><strong>Tên file:</strong> ${file.name}</p>
                 <p><strong>Kích thước:</strong> ${(file.size/1024).toFixed(2)} KB</p>
                 <p><strong>Tổng số dòng:</strong> ${json.length}</p>
                 <p><strong>Số cột:</strong> ${Object.keys(json[0]||{}).length}</p>`;
}

function displayPreview(rows){
  const p=document.getElementById('previewTable');
  if(!rows||rows.length===0){ p.innerHTML=''; return; }
  const cols=Object.keys(rows[0]);
  let html='<h5>Preview (5 dòng đầu):</h5><table class="preview-table"><thead><tr>';
  cols.forEach(c=> html+=`<th>${c}</th>` );
  html+='</tr></thead><tbody>';
  rows.forEach(r=>{ html+='<tr>'; cols.forEach(c=> html+=`<td>${r[c]??''}</td>` ); html+='</tr>'; });
  html+='</tbody></table>'; p.innerHTML=html;
}

function getFirstAvailable(row, keys){ for(const k of keys){ if(row[k]!==undefined && row[k]!==null && row[k]!=='' ) return row[k]; } return undefined; }

function extractShapeData(row, shape, group){
  const d={}; if(!shape) return d;
  if(shape==='Điểm'){ const v=getFirstAvailable(row, COLUMN_ALIASES.point[group]); if(v!==undefined) d.point_input=String(v); }
  else if(shape==='Đường thẳng'){ const p=getFirstAvailable(row,COLUMN_ALIASES.line_point[group]); const v=getFirstAvailable(row,COLUMN_ALIASES.line_vec[group]); if(p!==undefined) d[`line_A${group==='A'?1:2}`]=String(p); if(v!==undefined) d[`line_X${group==='A'?1:2}`]=String(v); }
  else if(shape==='Mặt phẳng'){ const a=getFirstAvailable(row,COLUMN_ALIASES.plane[group]); const b=getFirstAvailable(row,COLUMN_ALIASES.planeb[group]); const c=getFirstAvailable(row,COLUMN_ALIASES.planec[group]); const dd=getFirstAvailable(row,COLUMN_ALIASES.planed[group]); if(a!==undefined) d.plane_a=String(a); if(b!==undefined) d.plane_b=String(b); if(c!==undefined) d.plane_c=String(c); if(dd!==undefined) d.plane_d=String(dd); }
  else if(shape==='Đường tròn'){ const c=getFirstAvailable(row,COLUMN_ALIASES.circle_center[group]); const r=getFirstAvailable(row,COLUMN_ALIASES.circle_radius[group]); if(c!==undefined) d.circle_center=String(c); if(r!==undefined) d.circle_radius=String(r); }
  else if(shape==='Mặt cầu'){ const c=getFirstAvailable(row,COLUMN_ALIASES.sphere_center[group]); const r=getFirstAvailable(row,COLUMN_ALIASES.sphere_radius[group]); if(c!==undefined) d.sphere_center=String(c); if(r!==undefined) d.sphere_radius=String(r); }
  return d;
}

async function processBatchChunked(){
  const op=document.getElementById('batchOperation').value;
  const sA=document.getElementById('batchShapeA').value;
  const sB=document.getElementById('batchShapeB').value;
  if(!op||!sA||excelJsonData.length===0){ showError('Thiếu dữ liệu batch'); return; }
  const chunkSize=Math.max(10, Math.min(1000, parseInt(document.getElementById('chunkSize').value||'100',10)));
  const total=excelJsonData.length; const results=new Array(total).fill(null); const errors=[];
  document.getElementById('batchProgress').style.display='block';
  for(let i=0;i<total;i+=chunkSize){
    const end=Math.min(i+chunkSize,total);
    const calcs=excelJsonData.slice(i,end).map(row=>({
      operation:op,
      shape_A:sA,
      data_A:extractShapeData(row,sA,'A'),
      shape_B:sB||undefined,
      data_B:sB?extractShapeData(row,sB,'B'):undefined,
    }));
    let attempt=0; while(attempt<3){
      try{
        const res=await fetch(`${API_BASE}/api/geometry/batch`,{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({calculations:calcs})});
        const r=await res.json();
        for(let j=0;j<calcs.length;j++){ results[i+j]=r.data? r.data[j]: null; }
        break;
      }catch(e){ attempt++; if(attempt>=3){ errors.push(`Chunk ${i}-${end} failed: ${e.message}`); for(let j=0;j<calcs.length;j++){ results[i+j]=null; } } }
    }
    const percent=Math.round(((end)/total)*100); document.getElementById('progressFill').style.width=percent+'%'; document.getElementById('progressText').textContent=percent+'%';
  }
  document.getElementById('batchResults').style.display='block';
  const ok=results.filter(x=>x&&x.keylog).length; const err=total-ok;
  document.getElementById('batchSummary').innerHTML=`<p><strong>Tổng số dòng:</strong> ${total}</p><p><strong>Xử lý thành công:</strong> ${ok}</p><p><strong>Lỗi:</strong> ${err}</p>${errors.length?`<p><strong>Chunk errors:</strong> ${errors.length}</p>`:''}`;
  exportResultsToExcel({data:results});
}

function exportResultsToExcel(r){
  try{ const rows=[]; for(let i=0;i<excelJsonData.length;i++){ const src=excelJsonData[i]; const item=r.data[i]; rows.push({...src, keylog: item&&item.keylog?item.keylog:''}); } const ws=XLSX.utils.json_to_sheet(rows); const wb=XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, ws, 'Results'); XLSX.writeFile(wb,'geometry_results.xlsx'); }catch(e){ console.error('Export error:',e); }
}
