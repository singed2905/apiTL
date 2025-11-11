// Fix malformed template strings (placeholder typos) and ensure functions are defined before exposing
const API_BASE='http://localhost:5000';
let availableShapes=[]; let availableOperations=[]; let excelJsonData=[];

async function initApp(){
  try{
    const [s,o]=await Promise.all([
      fetch(`${API_BASE}/api/geometry/shapes`),
      fetch(`${API_BASE}/api/geometry/operations`)
    ]);
    const sd=await s.json(); const od=await o.json();
    availableShapes=sd.data||[]; availableOperations=od.data||[];
    populateOperations(); populateShapes();
    setupDynamicShapeDropdownFilter(); // add
  }catch(e){ showError('Không thể kết nối đến API.'); }
}
function populateOperations(){ const sel=document.getElementById('operation'); sel.innerHTML='<option value="">Chọn phép toán...</option>'; (availableOperations||[]).forEach(op=>{ const o=document.createElement('option'); o.value=op; o.textContent=op; sel.appendChild(o); }); }
function populateShapes(){ const a=document.getElementById('shapeA'), b=document.getElementById('shapeB'); a.innerHTML='<option value="">Chọn hình A...</option>'; b.innerHTML='<option value="">Không có</option>'; (availableShapes||[]).forEach(s=>{ const oa=document.createElement('option'); oa.value=s; oa.textContent=s; a.appendChild(oa); const ob=document.createElement('option'); ob.value=s; ob.textContent=s; b.appendChild(ob); }); }

function setupDynamicShapeDropdownFilter(){
  const opSel = document.getElementById('operation');
  opSel.addEventListener('change', ()=> updateShapeOptions());
  updateShapeOptions();
}

function updateShapeOptions(){
  const op = document.getElementById('operation').value;
  const a = document.getElementById('shapeA');
  const b = document.getElementById('shapeB');
  // Default: show all
  let shapeAOpts = [...availableShapes], shapeBOpts = [...availableShapes];
  let showA = true, showB = true;

  // Custom logic
  if(op==="Tương giao"||op==="Khoảng cách"){
    shapeAOpts = [...availableShapes];
    shapeBOpts = [...availableShapes];
    showA = showB = true;
  } else if(op==="Diện tích"){
    shapeAOpts = ["Đường tròn", "Mặt cầu"];
    shapeBOpts = [];
    showA = true; showB = false;
  } else if(op==="PT đường thẳng"){
    shapeAOpts = ["Điểm"];
    shapeBOpts = ["Điểm"];
    showA = showB = true;
  } else if(op==="Thể tích"){
    shapeAOpts = ["Mặt cầu"];
    shapeBOpts = [];
    showA = true; showB = false;
  }

  // Populate dropdowns
  a.innerHTML='<option value="">Chọn hình A...</option>';
  shapeAOpts.forEach(s=>{ const o=document.createElement('option'); o.value=s; o.textContent=s; a.appendChild(o); });
  b.innerHTML= '<option value="">Không có</option>';
  shapeBOpts.forEach(s=>{ const o=document.createElement('option'); o.value=s; o.textContent=s; b.appendChild(o); });

  // Hiện/ẩn các input group hình theo từng operation
  a.parentElement.style.display = showA ? "" : "none";
  document.getElementById('inputsA').style.display = showA ? "" : "none";
  b.parentElement.style.display = showB ? "" : "none";
  document.getElementById('inputsB').style.display = showB ? "" : "none";

  // Reset input fields for nhóm hidden
  if(!showB){ b.value = ""; document.getElementById('inputsB').innerHTML = ""; }
  if(!showA){ a.value = ""; document.getElementById('inputsA').innerHTML = ""; }
  // Auto-update fields after option filtering
  updateInputFields();
}

function updateInputFields(){ const a=document.getElementById('shapeA').value; const b=document.getElementById('shapeB').value; updateShapeInputs('A',a); updateShapeInputs('B',b); }
function updateShapeInputs(g,s){ const c=document.getElementById(`inputs${g}`); c.innerHTML=''; if(!s){ c.classList.remove('active'); return; } c.classList.add('active'); if(s==='Điểm'){ c.innerHTML=`<label>Tọa độ (x,y,z):</label><input type="text" id="point_input_${g}" placeholder="1,2,3">`; } else if(s==='Đường thẳng'){ c.innerHTML=`<label>Điểm trên đường thẳng (x,y,z):</label><input type="text" id="line_A${g==='A'?'1':'2'}_${g}" placeholder="0,0,0"><label style="margin-top:10px;">Vector chỉ phương (dx,dy,dz):</label><input type="text" id="line_X${g==='A'?'1':'2'}_${g}" placeholder="1,1,1">`; } else if(s==='Mặt phẳng'){ c.innerHTML=`<label>a, b, c, d:</label><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px"><input id="plane_a_${g}" placeholder="a"><input id="plane_b_${g}" placeholder="b"><input id="plane_c_${g}" placeholder="c"><input id="plane_d_${g}" placeholder="d"></div>`; } else if(s==='Đường tròn'){ c.innerHTML=`<label>Tâm (x,y):</label><input id="circle_center_${g}" placeholder="0,0"><label style="margin-top:10px;">Bán kính:</label><input id="circle_radius_${g}" placeholder="5">`; } else if(s==='Mặt cầu'){ c.innerHTML=`<label>Tâm (x,y,z):</label><input id="sphere_center_${g}" placeholder="0,0,0"><label style="margin-top:10px;">Bán kính:</label><input id="sphere_radius_${g}" placeholder="3">`; } }

function collectInputData(group, shape){ const d={}; if(shape==='Điểm'){ const v=document.getElementById(`point_input_${group}`); if(v) d.point_input=v.value; } else if(shape==='Đường thẳng'){ const la=document.getElementById(`line_A${group==='A'?'1':'2'}_${group}`); const lx=document.getElementById(`line_X${group==='A'?'1':'2'}_${group}`); if(la) d[`line_A${group==='A'?'1':'2'}`]=la.value; if(lx) d[`line_X${group==='A'?'1':'2'}`]=lx.value; } else if(shape==='Mặt phẳng'){ ['a','b','c','d'].forEach(k=>{ const el=document.getElementById(`plane_${k}_${group}`); if(el) d[`plane_${k}`]=el.value; }); } else if(shape==='Đường tròn'){ const cc=document.getElementById(`circle_center_${group}`); const cr=document.getElementById(`circle_radius_${group}`); if(cc) d.circle_center=cc.value; if(cr) d.circle_radius=cr.value; } else if(shape==='Mặt cầu'){ const sc=document.getElementById(`sphere_center_${group}`); const sr=document.getElementById(`sphere_radius_${group}`); if(sc) d.sphere_center=sc.value; if(sr) d.sphere_radius=sr.value; } return d; }

async function processGeometry(){ const operation=document.getElementById('operation').value; const shapeA=document.getElementById('shapeA').value; const shapeB=document.getElementById('shapeB').value; const version=document.getElementById('version').value; if(!operation||!shapeA){ showError('Vui lòng chọn phép toán và hình A.'); return; } const dataA=collectInputData('A',shapeA); const dataB=shapeB?collectInputData('B',shapeB):{}; const body={operation, shape_A:shapeA, data_A:dataA, version}; if(shapeB){ body.shape_B=shapeB; body.data_B=dataB; } setLoading(true); try{ const res=await fetch(`${API_BASE}/api/geometry/process`,{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)}); const r=await res.json(); if(r.status==='success') displayResults(r.data); else showError(r.message||'Xử lý thất bại'); }catch(e){ showError('Lỗi kết nối đến API: '+e.message); } finally { setLoading(false); } }

function setLoading(on){ document.getElementById('processBtn').disabled=on; if(on){ document.getElementById('results').innerHTML='<div class="loading">🔄 Đang xử lý...</div>'; } }
function displayResults(data){ const el=document.getElementById('results'); el.innerHTML=`<div class="result-item"><h4>🔑 Keylog (${data.version}):</h4><div class="keylog">${data.keylog}<button class="copy-btn" onclick="copyToClipboard('${data.keylog}')">Copy</button></div></div><div class="result-item"><h4>📝 Thông tin:</h4><p><strong>Phép toán:</strong> ${data.operation}</p><p><strong>Hình A:</strong> ${data.shape_A}</p>${data.shape_B?`<p><strong>Hình B:</strong> ${data.shape_B}</p>`:''}<p><strong>Mã hóa A:</strong> [${(data.encoded_A||[]).join(', ')}]</p>${(data.encoded_B&&data.encoded_B.length>0)?`<p><strong>Mã hóa B:</strong> ${data.encoded_B.join(', ')}</p>`:''}</div><div class="success">✅ Xử lý thành công!</div>`; }
function showError(m){ document.getElementById('results').innerHTML=`<div class="error">❌ ${m}</div>`; }
function copyToClipboard(t){ navigator.clipboard.writeText(t).then(()=>{ const b=event.target; const o=b.textContent; b.textContent='Copied!'; b.style.background='#27ae60'; setTimeout(()=>{ b.textContent=o; b.style.background='#3498db'; },1500); }).catch(()=>alert('Không thể copy.')); }
