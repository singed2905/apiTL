const NEW_OPERATION = 'Phương trình đường thẳng';

function addLineEquationOperation() {
    // Inject operation into dropdown when app initializes
    const opSelect = document.getElementById('operation');
    if (!opSelect) return;
    const hasOption = Array.from(opSelect.options).some(o => o.value === NEW_OPERATION);
    if (!hasOption) {
        const opt = document.createElement('option');
        opt.value = NEW_OPERATION;
        opt.textContent = NEW_OPERATION;
        opSelect.appendChild(opt);
    }
}

function lineFromTwoPoints(p1, p2) {
    // Return slope-intercept form y = ax + b, and parametric for 3D
    const dx = p2.x - p1.x;
    const dy = p2.y - p1.y;
    const dz = (p2.z || 0) - (p1.z || 0);
    const is3D = (p1.z || 0) !== 0 || (p2.z || 0) !== 0;

    if (!is3D) {
        if (dx === 0) {
            return { type: 'vertical', equation: `x = ${p1.x}` };
        }
        const a = dy / dx;
        const b = p1.y - a * p1.x;
        const aStr = Number.isFinite(a) ? a.toFixed(6).replace(/\.0+$/, '') : a;
        const bStr = Number.isFinite(b) ? b.toFixed(6).replace(/\.0+$/, '') : b;
        return { type: '2d', equation: `y = ${aStr}x ${b>=0?'+':'-'} ${Math.abs(bStr)}` };
    }

    // Parametric 3D
    return {
        type: '3d',
        equation: `(x,y,z) = (${p1.x}, ${p1.y}, ${p1.z||0}) + t(${dx}, ${dy}, ${dz})`
    };
}

function handleLineEquationManual() {
    const op = document.getElementById('operation').value;
    if (op !== NEW_OPERATION) return;

    // Force shapes to Điểm/Điểm
    document.getElementById('shapeA').value = 'Điểm';
    document.getElementById('shapeB').value = 'Điểm';
    updateInputFields();

    const objA = parseShape('A', 'Điểm');
    const objB = parseShape('B', 'Điểm');
    if (!objA || !objB) return;

    // Render line through two points
    currentView = (objA.z!==0 || objB.z!==0) ? '3D' : '2D';
    updateVisualization();

    // Compute and show equation locally (no API)
    const eq = lineFromTwoPoints(objA, objB);
    const resultsContainer = document.getElementById('results');
    const html = `
        <div class="result-item">
            <h4>📐 Phương trình đường thẳng:</h4>
            <p style="font-family:monospace;font-size:16px;">${eq.equation}</p>
        </div>
        <div class="result-item">
            <h4>🧩 Dữ liệu:</h4>
            <p><strong>Điểm A:</strong> (${objA.x}, ${objA.y}${objA.z?`, ${objA.z}`:''})</p>
            <p><strong>Điểm B:</strong> (${objB.x}, ${objB.y}${objB.z?`, ${objB.z}`:''})</p>
        </div>`;
    resultsContainer.innerHTML = html;
}

// Hook into input changes to recompute equation in manual mode
(function attachManualEquationHooks(){
    window.addEventListener('load', ()=>{
        addLineEquationOperation();
        document.addEventListener('input', (e)=>{
            if (e.target && (e.target.id.includes('point_input_A') || e.target.id.includes('point_input_B'))) {
                handleLineEquationManual();
            }
        });
        document.getElementById('operation').addEventListener('change', handleLineEquationManual);
    });
})();
