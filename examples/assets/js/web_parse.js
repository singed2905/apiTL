// Parsers to convert current form inputs into geometry objects usable by visualization
function parseCurrentGeometry(){
  const a=document.getElementById('shapeA').value; const b=document.getElementById('shapeB').value;
  return { objA: parseShape('A', a), objB: parseShape('B', b) };
}

function parseShape(group, shape){
  if(!shape) return null;
  const data = collectInputData(group, shape);
  if(shape==='Điểm'){
    const v=(data.point_input||'').trim(); if(!v) return null; const p=v.split(',').map(s=>parseFloat(s.trim())).filter(n=>!isNaN(n)); if(p.length<2) return null; return { type:'point', x:p[0], y:p[1], z:p[2]||0 };
  }
  if(shape==='Đường thẳng'){
    const pa=(data[`line_A${group==='A'?'1':'2'}`]||'').trim(); const vx=(data[`line_X${group==='A'?'1':'2'}`]||'').trim(); if(!pa||!vx) return null; const P=pa.split(',').map(s=>parseFloat(s.trim())).filter(n=>!isNaN(n)); const V=vx.split(',').map(s=>parseFloat(s.trim())).filter(n=>!isNaN(n)); if(P.length<2||V.length<2) return null; const is3 = (P[2]&&P[2]!==0)||(V[2]&&V[2]!==0)||P.length>=3||V.length>=3; return { type:is3?'line3d':'line', point:{x:P[0],y:P[1],z:P[2]||0}, vector:{x:V[0],y:V[1],z:V[2]||0} };
  }
  if(shape==='Mặt phẳng'){
    const a=parseFloat((data.plane_a||'').trim()); const b=parseFloat((data.plane_b||'').trim()); const c=parseFloat((data.plane_c||'').trim()); const d=parseFloat((data.plane_d||'').trim()); if([a,b,c,d].some(x=>isNaN(x))) return null; if(a===0&&b===0&&c===0) return null; return { type:'plane', a,b,c,d };
  }
  if(shape==='Đường tròn'){
    const cc=(data.circle_center||'').trim(); const r=parseFloat((data.circle_radius||'').trim()); if(!cc||isNaN(r)||r<=0) return null; const C=cc.split(',').map(s=>parseFloat(s.trim())).filter(n=>!isNaN(n)); if(C.length<2) return null; return { type:'circle', center:{x:C[0],y:C[1]}, radius:r };
  }
  if(shape==='Mặt cầu'){
    const cc=(data.sphere_center||'').trim(); const r=parseFloat((data.sphere_radius||'').trim()); if(!cc||isNaN(r)||r<=0) return null; const C=cc.split(',').map(s=>parseFloat(s.trim())).filter(n=>!isNaN(n)); if(C.length<3) return null; return { type:'sphere', center:{x:C[0],y:C[1],z:C[2]}, radius:r };
  }
  return null;
}

// Expose for visualization module
window.parseShape = parseShape;
window.parseCurrentGeometry = parseCurrentGeometry;
