// Visualization module for 2D/3D using Plotly (v2.x)
let currentView='2D';
let plotInitialized=false;

function setupVisualization(){
  const el=document.getElementById('geometryPlot');
  if(!el) return;
  const layout2D={ title:'Geometry Visualization', xaxis:{title:'X',zeroline:true,showgrid:true}, yaxis:{title:'Y',zeroline:true,showgrid:true,scaleanchor:'x'}, showlegend:true, margin:{t:40,r:30,b:40,l:40} };
  Plotly.newPlot('geometryPlot',[],layout2D,{responsive:true});
  plotInitialized=true;
}

function needs3D(objA,objB){
  const has3D=(o)=>{ if(!o) return false; return o.type==='line3d'||o.type==='plane'||o.type==='sphere'||(o.type==='point'&&o.z&&o.z!==0); };
  return has3D(objA)||has3D(objB);
}

function parseCurrentObjects(){
  const a=document.getElementById('shapeA').value; const b=document.getElementById('shapeB').value;
  const objA=parseShape('A',a); const objB=parseShape('B',b);
  return {objA,objB};
}

function updateVisualization(){
  if(!plotInitialized) return;
  const {objA,objB}=parseCurrentObjects();
  const op=document.getElementById('operation').value;
  const is3D=needs3D(objA,objB);
  if(is3D && currentView!=='3D') currentView='3D';
  if(!is3D && currentView!=='2D') currentView='2D';
  if(currentView==='3D') render3D(objA,objB,op); else render2D(objA,objB,op);
}

function render2D(objA,objB,op){
  const traces=[];
  if(objA){ const t=createTrace2D(objA,'#2196F3','Shape A'); if(t) traces.push(t); }
  if(objB){ const t=createTrace2D(objB,'#f44336','Shape B'); if(t) traces.push(t); }
  const layout={ title:`Geometry Visualization (2D) - ${op||'Manual'}`, xaxis:{title:'X'}, yaxis:{title:'Y',scaleanchor:'x'}, showlegend:true };
  Plotly.react('geometryPlot',traces,layout);
}

function render3D(objA,objB,op){
  const traces=[];
  if(objA){ const t=createTrace3D(objA,'#2196F3','Shape A'); if(t) traces.push(t); }
  if(objB){ const t=createTrace3D(objB,'#f44336','Shape B'); if(t) traces.push(t); }
  const layout={ title:`Geometry Visualization (3D) - ${op||'Manual'}`, scene:{ xaxis:{title:'X'}, yaxis:{title:'Y'}, zaxis:{title:'Z'} }, showlegend:true };
  Plotly.react('geometryPlot',traces,layout);
}

function createTrace2D(obj,color,name){
  if(!obj) return null;
  if(obj.type==='point'){
    return { x:[obj.x], y:[obj.y], mode:'markers', type:'scatter', marker:{size:10,color}, name:`${name} (${obj.x}, ${obj.y})` };
  }
  if(obj.type==='line'){
    const range=10; const t=[-range,range];
    const x=t.map(v=>obj.point.x+v*obj.vector.x);
    const y=t.map(v=>obj.point.y+v*obj.vector.y);
    return { x, y, mode:'lines', type:'scatter', line:{color,width:3}, name };
  }
  if(obj.type==='circle'){
    const th=Array.from({length:100},(_,i)=>2*Math.PI*i/99);
    const x=th.map(t=>obj.center.x+obj.radius*Math.cos(t));
    const y=th.map(t=>obj.center.y+obj.radius*Math.sin(t));
    return { x:[...x,x[0]], y:[...y,y[0]], mode:'lines', type:'scatter', line:{color,width:3}, fill:'toself', fillcolor:color, opacity:0.2, name:`${name} (r=${obj.radius})` };
  }
  return null;
}

function createTrace3D(obj,color,name){
  if(!obj) return null;
  if(obj.type==='point'){
    return { x:[obj.x], y:[obj.y], z:[obj.z||0], mode:'markers', type:'scatter3d', marker:{size:5,color}, name:`${name} (${obj.x}, ${obj.y}, ${obj.z||0})` };
  }
  if(obj.type==='line3d'){
    const t=Array.from({length:30},(_,i)=>i-15);
    const x=t.map(v=>obj.point.x+v*obj.vector.x);
    const y=t.map(v=>obj.point.y+v*obj.vector.y);
    const z=t.map(v=>obj.point.z+v*obj.vector.z);
    return { x,y,z, mode:'lines', type:'scatter3d', line:{color,width:6}, name };
  }
  if(obj.type==='plane'){
    const range=5, step=0.5; const x=[],y=[],z=[];
    for(let i=-range;i<=range;i+=step){ for(let j=-range;j<=range;j+=step){ x.push(i); y.push(j); z.push(obj.c!==0?-(obj.a*i+obj.b*j+obj.d)/obj.c:0); } }
    return { x,y,z, mode:'markers', type:'scatter3d', marker:{size:2,color,opacity:0.6}, name:`${name} (${obj.a}x+${obj.b}y+${obj.c}z+${obj.d}=0)` };
  }
  if(obj.type==='sphere'){
    const phi=Array.from({length:20},(_,i)=>i*Math.PI/19); const th=Array.from({length:20},(_,i)=>i*2*Math.PI/19);
    const x=[],y=[],z=[]; phi.forEach(p=>{ th.forEach(t=>{ x.push(obj.center.x+obj.radius*Math.sin(p)*Math.cos(t)); y.push(obj.center.y+obj.radius*Math.sin(p)*Math.sin(t)); z.push(obj.center.z+obj.radius*Math.cos(p)); }); });
    return { x,y,z, mode:'markers', type:'scatter3d', marker:{size:2,color,opacity:0.8}, name:`${name} (r=${obj.radius})` };
  }
  return null;
}

function resetView(){ if(!plotInitialized) return; Plotly.relayout('geometryPlot',{ 'xaxis.autorange':true,'yaxis.autorange':true,'scene.camera':{eye:{x:1.25,y:1.25,z:1.25}} }); }
function toggle3D(){ currentView=currentView==='2D'?'3D':'2D'; updateVisualization(); }

// Expose globals
window.updateVisualization=updateVisualization;
window.resetView=resetView;
window.toggle3D=toggle3D;
window.setupVisualization=setupVisualization;
