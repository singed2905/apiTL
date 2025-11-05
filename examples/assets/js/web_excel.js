// Excel batch processing extracted from web_example.html (working inline version)
const COLUMN_ALIASES={
  plane:{ A:['plane_a','P1_a'], B:['plane_a','P2_a'] },
  planeb:{ A:['plane_b','P1_b'], B:['plane_b','P2_b'] },
  planec:{ A:['plane_c','P1_c'], B:['plane_c','P2_c'] },
  planed:{ A:['plane_d','P1_d'], B:['plane_d','P2_d'] },
  line_point:{ A:['line_A1','d_P_data_A','P1_P'], B:['line_A2','d_P_data_B','P2_P'] },
  line_vec:{ A:['line_X1','d_V_data_A','P1_V'], B:['line_X2','d_V_data_B','P2_V'] },
  point:{ A:['point_input','data_A','P1'], B:['point_input','data_B','P2'] },
  circle_center:{ A:['circle_center','c_center_A','C1_center'], B:['circle_center','c_center_B','C2_center'] },
  circle_radius:{ A:['circle_radius','c_radius_A','C1_radius'], B:['circle_radius','c_radius_B','C2_radius'] },
  sphere_center:{ A:['sphere_center','s_center_A','S1_center'], B:['sphere_center','s_center_B','S2_center'] },
  sphere_radius:{ A:['sphere_radius','s_radius_A','S1_radius'], B:['sphere_radius','s_radius_B','S2_radius'] },
};
const SHAPE_TEMPLATES={
  'Điểm':{ required:['point'] },
  'Đường thẳng':{ required:['line_point','line_vec'] },
  'Mặt phẳng':{ required:['plane','planeb','planec','planed'] },
  'Đường tròn':{ required:['circle_center','circle_radius'] },
  'Mặt cầu':{ required:['sphere_center','sphere_radius'] },
};

function readExcelFile(file){
  return new Promise((resolve,reject)=>{
    const reader=new FileReader();
    reader.onload=e=>{ try{ const data=new Uint8Array(e.target.result); const wb=XLSX.read(data,{type:'array'}); const ws=wb.Sheets[wb.SheetNames[0]]; const json=XLSX.utils.sheet_to_json(ws,{defval:''}); resolve(json); }catch(err){ reject(err); } };
    reader.onerror=reject; reader.readAsArrayBuffer(file);
  });
}

function populateBatchConfig(){
  const opSel=document.getElementById('batchOperation');
  const aSel=document.getElementById('batchShapeA');
  const bSel=document.getElementById('batchShapeB');
  opSel.innerHTML='<option value="">Chọn phép toán...</option>';
  (availableOperations||[]).forEach(op=>{ const o=document.createElement('option'); o.value=op; o.textContent=op; opSel.appendChild(o); });
  const shapes=['(Auto)', ...(availableShapes||[])];
  aSel.innerHTML=''; bSel.innerHTML='';
  shapes.forEach(s=>{ const o1=document.createElement('option'); o1.value=s; o1.textContent=s; aSel.appendChild(o1); const o2=document.createElement('option'); o2.value=s; o2.textContent=s; bSel.appendChild(o2); });
  aSel.value='(Auto)'; bSel.value='(Auto)';
}

function autoDetectShape(columns, group){
  const hasPlane=['a','b','c','d'].every(k=> columns.includes(`${group==='A'?'P1':'P2'}_${k}`) || columns.includes(`plane_${k}`)); if(hasPlane) return 'Mặt phẳng';
  const hasLine=(columns.some(c=> c===`line_A${group==='A'?1:2}` || c===`d_P_data_${group}` || c===`${group==='A'?'P1':'P2'}_P`)) && (columns.some(c=> c===`line_X${group==='A'?1:2}` || c===`d_V_data_${group}` || c===`${group==='A'?'P1':'P2'}_V`)); if(hasLine) return 'Đường thẳng';
  const hasPoint=columns.some(c=> c==='point_input' || c===(group==='A'?'data_A':'data_B') || c===(group==='A'?'P1':'P2')); if(hasPoint) return 'Điểm';
  const hasCircle=columns.some(c=> ['circle_center','c_center_A','c_center_B','C1_center','C2_center'].includes(c)) && columns.some(c=> ['circle_radius','c_radius_A','c_radius_B','C1_radius','C2_radius'].includes(c)); if(hasCircle) return 'Đường tròn';
  const hasSphere=columns.some(c=> ['sphere_center','s_center_A','s_center_B','S1_center','S2_center'].includes(c)) && columns.some(c=> ['sphere_radius','s_radius_A','s_radius_B','S1_radius','S2_radius'].includes(c)); if(hasSphere) return 'Mặt cầu';
  return '';
}

function validateExcelStructure(json, operation, shapeA, shapeB){
  const out={valid:true, errors:[], detected_columns:[], effective:{}}; if(!json||json.length===0){ out.valid=false; out.errors.push('File Excel trống'); return out; }
  const cols=Object.keys(json[0]); out.detected_columns=cols;
  const effA = shapeA==='(Auto)' ? autoDetectShape(cols,'A') : shapeA;
  const effB = shapeB==='(Auto)' ? autoDetectShape(cols,'B') : shapeB;
  const check=(shape,group)=>{ const t=SHAPE_TEMPLATES[shape]; if(!t) return; t.required.forEach(token=>{ const aliases=COLUMN_ALIASES[token][group]; const found=aliases.some(k=> cols.includes(k)); if(!found){ out.valid=false; out.errors.push(`${shape} (${group}) thiếu cột: ${aliases.join(' | ')}`); } }); };
  if(effA) check(effA,'A'); if(effB && !['Diện tích','Thể tích'].includes(operation)) check(effB,'B');
  out.effective={shapeA:effA||shapeA, shapeB:effB||shapeB};
  return out;
}

function displayValidationResults(v){ const c=document.getElementById('validationResults'); let h='<div class="validation-summary">'; h+= v.valid?'<div class="success">✅ File Excel hợp lệ theo mapping!</div>':'<div class="error">❌ File Excel chưa khớp mapping</div>'; h+=`<div class="detected-columns"><h5>📋 Các cột:</h5><div class="column-list">${v.detected_columns.join(', ')}</div></div>`; if(v.effective){ h+=`<div style="margin-top:8px;font-size:13px;color:#555">Dùng cấu hình: Hình A = <b>${v.effective.shapeA||'-'}</b>, Hình B = <b>${v.effective.shapeB||'-'}</b></div>`; } if(v.errors.length>0){ h+='<div class="validation-errors"><h5>🚨 Lỗi:</h5><ul>'; v.errors.forEach(e=> h+=`<li>${e}</li>` ); h+='</ul></div>'; } h+='</div>'; c.innerHTML=h; }

function displayFileDetails(file, json){ const c=document.getElementById('fileDetails'); c.innerHTML = `<p><strong>Tên file:</strong> ${file.name}</p><p><strong>Kích thước:</strong> ${(file.size/1024).toFixed(2)} KB</p><p><strong>Tổng số dòng:</strong> ${json.length}</p><p><strong>Số cột:</strong> ${Object.keys(json[0]||{}).length}</p>`; }
function displayPreview(rows){ const p=document.getElementById('previewTable'); if(!rows||rows.length===0){ p.innerHTML=''; return; } const cols=Object.keys(rows[0]); let html='<h5>Preview (5 dòng đầu):</h5><table class="preview-table"><thead><tr>'; cols.forEach(c=> html+=`<th>${c}</th>` ); html+='</tr></thead><tbody>'; rows.forEach(r=>{ html+='<tr>'; cols.forEach(c=> html+=`<td>${r[c]??''}</td>` ); html+='</tr>'; }); html+='</tbody></table>'; p.innerHTML=html; }

async function handleExcelLocal(){ const f=document.getElementById('excelFile').files[0]; if(!f) return; try{ const json=await readExcelFile(f); excelJsonData=json; document.getElementById('fileInfo').style.display='block'; document.getElementById('processingConfig').style.display='block'; populateBatchConfig(); const v=validateExcelStructure(json, document.getElementById('batchOperation').value, document.getElementById('batchShapeA').value, document.getElementById('batchShapeB').value); displayValidationResults(v); displayFileDetails(f, json); displayPreview(json.slice(0,5)); document.getElementById('processBatchBtn').disabled=!v.valid; }catch(e){ showError('Không đọc được file Excel: '+e.message); }
}

function extractShapeData(row, shape, group){ const d={}; if(!shape) return d; if(shape==='Điểm'){ const v=getFirstAvailable(row, COLUMN_ALIASES.point[group]); if(v!==undefined) d.point_input=String(v); } else if(shape==='Đường thẳng'){ const p=getFirstAvailable(row,COLUMN_ALIASES.line_point[group]); const v=getFirstAvailable(row,COLUMN_ALIASES.line_vec[group]); if(p!==undefined) d[`line_A${group==='A'?1:2}`]=String(p); if(v!==undefined) d[`line_X${group==='A'?1:2}`]=String(v); } else if(shape==='Mặt phẳng'){ const a=getFirstAvailable(row,COLUMN_ALIASES.plane[group]); const b=getFirstAvailable(row,COLUMN_ALIASES.planeb[group]); const c=getFirstAvailable(row,COLUMN_ALIASES.planec[group]); const dd=getFirstAvailable(row,COLUMN_ALIASES.planed[group]); if(a!==undefined) d.plane_a=String(a); if(b!==undefined) d.plane_b=String(b); if(c!==undefined) d.plane_c=String(c); if(dd!==undefined) d.plane_d=String(dd); } else if(shape==='Đường tròn'){ const c=getFirstAvailable(row,COLUMN_ALIASES.circle_center[group]); const r=getFirstAvailable(row,COLUMN_ALIASES.circle_radius[group]); if(c!==undefined) d.circle_center=String(c); if(r!==undefined) d.circle_radius=String(r); } else if(shape==='Mặt cầu'){ const c=getFirstAvailable(row,COLUMN_ALIASES.sphere_center[group]); const r=getFirstAvailable(row,COLUMN_ALIASES.sphere_radius[group]); if(c!==undefined) d.sphere_center=String(c); if(r!==undefined) d.sphere_radius=String(r); } return d; }

async function processBatchChunked(){ const op=document.getElementById('batchOperation').value; let sA=document.getElementById('batchShapeA').value; let sB=document.getElementById('batchShapeB').value; if(!op){ showError('Chọn phép toán cho batch'); return; } if(!excelJsonData||excelJsonData.length===0){ showError('Chưa có dữ liệu Excel'); return; } const cols=Object.keys(excelJsonData[0]||{}); if(sA==='(Auto)') sA=autoDetectShape(cols,'A'); if(sB==='(Auto)') sB=autoDetectShape(cols,'B'); if(!sA){ showError('Không nhận diện được Hình A'); return;} if(!['Diện tích','Thể tích'].includes(op) && !sB){ showError('Không nhận diện được Hình B'); return;} const chunkInput=document.getElementById('chunkSize'); const CHUNK_SIZE=Math.max(10, Math.min(1000, parseInt(chunkInput.value||'100',10))); const total=excelJsonData.length; const results=new Array(total).fill(null); const errors=[]; document.getElementById('batchProgress').style.display='block'; for(let i=0;i<total;i+=CHUNK_SIZE){ const end=Math.min(i+CHUNK_SIZE,total); const calcs=excelJsonData.slice(i,end).map(row=>({ operation:op, shape_A:sA, data_A:extractShapeData(row,sA,'A'), shape_B:sB||undefined, data_B:sB?extractShapeData(row,sB,'B'):undefined })); let attempt=0; while(attempt<3){ try{ const res=await fetch(`${API_BASE}/api/geometry/batch`,{ method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({calculations:calcs}) }); const r=await res.json(); for(let j=0;j<calcs.length;j++){ results[i+j]=r.data? r.data[j]: null; } break; }catch(e){ attempt++; if(attempt>=3){ errors.push(`Chunk ${i}-${end} failed: ${e.message}`); for(let j=0;j<calcs.length;j++){ results[i+j]=null; } } } } const percent=Math.round(((end)/total)*100); document.getElementById('progressFill').style.width=percent+'%'; document.getElementById('progressText').textContent=percent+'%'; }
 document.getElementById('batchResults').style.display='block'; const ok=results.filter(r=> r && r.keylog).length; const err=total-ok; document.getElementById('batchSummary').innerHTML=`<p><strong>Tổng số dòng:</strong> ${total}</p><p><strong>Xử lý thành công:</strong> ${ok}</p><p><strong>Lỗi:</strong> ${err}</p>${errors.length?`<p><strong>Chunk errors:</strong> ${errors.length}</p>`:''}`; exportResultsToExcel({data:results}); }

function exportResultsToExcel(r){ try{ const rows=[]; for(let i=0;i<excelJsonData.length;i++){ const src=excelJsonData[i]; const item=r.data[i]; rows.push({...src, keylog: item&&item.keylog?item.keylog:''}); } const ws=XLSX.utils.json_to_sheet(rows); const wb=XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, ws, 'Results'); XLSX.writeFile(wb, 'geometry_results.xlsx'); } catch(e){ console.error('Export error:', e); }
}
