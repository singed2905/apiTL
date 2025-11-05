let currentView = '2D';
let plotInitialized = false;

function setupVisualizationListeners() {
    // No need for manual listeners - inputs have oninput="updateVisualization()"
    console.log('Visualization listeners setup complete');
}

function initializeVisualization() {
    const layout2D = {
        title: 'Geometry Visualization',
        xaxis: { title: 'X', zeroline: true, showgrid: true },
        yaxis: { title: 'Y', zeroline: true, showgrid: true, scaleanchor: 'x' },
        showlegend: true,
        margin: { t: 50, r: 50, b: 50, l: 50 },
        hovermode: 'closest'
    };
    
    Plotly.newPlot('geometryPlot', [], layout2D, { responsive: true });
    plotInitialized = true;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

const debouncedVisualization = debounce(updateVisualization, 300);

function updateVisualization() {
    if (!plotInitialized) return;
    
    const { objA, objB } = parseCurrentGeometry();
    const operation = document.getElementById('operation').value;
    
    // Auto-detect 2D/3D
    const is3D = needsThreeDimensions(objA, objB);
    
    if (is3D && currentView !== '3D') {
        currentView = '3D';
        render3D(objA, objB, operation);
    } else if (!is3D && currentView !== '2D') {
        currentView = '2D';
        render2D(objA, objB, operation);
    } else {
        // Same view, just update traces
        if (currentView === '3D') {
            render3D(objA, objB, operation);
        } else {
            render2D(objA, objB, operation);
        }
    }
    
    // Update toggle button
    const btn = document.getElementById('toggle3DBtn');
    if (btn) btn.textContent = currentView === '2D' ? '🔄 Switch to 3D' : '🔄 Switch to 2D';
}

function needsThreeDimensions(objA, objB) {
    const has3D = (obj) => {
        if (!obj) return false;
        return obj.type === 'line3d' || obj.type === 'plane' || obj.type === 'sphere' || 
               (obj.type === 'point' && obj.z !== undefined && obj.z !== 0);
    };
    return has3D(objA) || has3D(objB);
}

function render2D(objA, objB, operation) {
    const traces = [];
    
    // Shape A
    if (objA) {
        const traceA = createTrace2D(objA, '#2196F3', 'Shape A');
        if (traceA) traces.push(traceA);
    }
    
    // Shape B
    if (objB) {
        const traceB = createTrace2D(objB, '#f44336', 'Shape B');
        if (traceB) traces.push(traceB);
    }
    
    // Operation result visualization
    if (objA && objB && operation) {
        const resultTrace = createOperationTrace2D(objA, objB, operation);
        if (resultTrace) traces.push(resultTrace);
    }
    
    const layout = {
        title: `Geometry Visualization (2D) - ${operation || 'Manual Input'}`,
        xaxis: { title: 'X', zeroline: true, showgrid: true },
        yaxis: { title: 'Y', zeroline: true, showgrid: true, scaleanchor: 'x' },
        showlegend: true,
        hovermode: 'closest'
    };
    
    Plotly.react('geometryPlot', traces, layout);
}

function render3D(objA, objB, operation) {
    const traces = [];
    
    // Shape A
    if (objA) {
        const traceA = createTrace3D(objA, '#2196F3', 'Shape A');
        if (traceA) traces.push(traceA);
    }
    
    // Shape B
    if (objB) {
        const traceB = createTrace3D(objB, '#f44336', 'Shape B');
        if (traceB) traces.push(traceB);
    }
    
    // Operation result
    if (objA && objB && operation) {
        const resultTrace = createOperationTrace3D(objA, objB, operation);
        if (resultTrace) traces.push(resultTrace);
    }
    
    const layout = {
        title: `Geometry Visualization (3D) - ${operation || 'Manual Input'}`,
        scene: {
            xaxis: { title: 'X' },
            yaxis: { title: 'Y' },
            zaxis: { title: 'Z' }
        },
        showlegend: true
    };
    
    Plotly.react('geometryPlot', traces, layout);
}

function createTrace2D(obj, color, name) {
    if (!obj) return null;
    
    if (obj.type === 'point') {
        return {
            x: [obj.x],
            y: [obj.y],
            mode: 'markers',
            type: 'scatter',
            marker: { size: 10, color: color, symbol: 'circle' },
            name: `${name} (${obj.x}, ${obj.y})`,
            hovertemplate: `${name}<br>X: %{x}<br>Y: %{y}<extra></extra>`
        };
    } else if (obj.type === 'line') {
        // Generate line segment
        const range = 10;
        const t = [-range, range];
        const x = t.map(val => obj.point.x + val * obj.vector.x);
        const y = t.map(val => obj.point.y + val * obj.vector.y);
        
        return {
            x: x,
            y: y,
            mode: 'lines',
            type: 'scatter',
            line: { color: color, width: 3 },
            name: name,
            hovertemplate: `${name}<br>Point: (${obj.point.x}, ${obj.point.y})<br>Vector: (${obj.vector.x}, ${obj.vector.y})<extra></extra>`
        };
    } else if (obj.type === 'circle') {
        // Generate circle
        const theta = Array.from({length: 100}, (_, i) => 2 * Math.PI * i / 99);
        const x = theta.map(t => obj.center.x + obj.radius * Math.cos(t));
        const y = theta.map(t => obj.center.y + obj.radius * Math.sin(t));
        
        return {
            x: [...x, x[0]], // Close the circle
            y: [...y, y[0]],
            mode: 'lines',
            type: 'scatter',
            line: { color: color, width: 3 },
            fill: 'toself',
            fillcolor: color,
            opacity: 0.2,
            name: `${name} (r=${obj.radius})`,
            hovertemplate: `${name}<br>Center: (${obj.center.x}, ${obj.center.y})<br>Radius: ${obj.radius}<extra></extra>`
        };
    }
    
    return null;
}

function createTrace3D(obj, color, name) {
    if (!obj) return null;
    
    if (obj.type === 'point') {
        return {
            x: [obj.x],
            y: [obj.y],
            z: [obj.z || 0],
            mode: 'markers',
            type: 'scatter3d',
            marker: { size: 8, color: color },
            name: `${name} (${obj.x}, ${obj.y}, ${obj.z || 0})`,
            hovertemplate: `${name}<br>X: %{x}<br>Y: %{y}<br>Z: %{z}<extra></extra>`
        };
    } else if (obj.type === 'line3d') {
        const range = 10;
        const t = Array.from({length: 20}, (_, i) => (i - 10));
        const x = t.map(val => obj.point.x + val * obj.vector.x);
        const y = t.map(val => obj.point.y + val * obj.vector.y);
        const z = t.map(val => obj.point.z + val * obj.vector.z);
        
        return {
            x: x, y: y, z: z,
            mode: 'lines',
            type: 'scatter3d',
            line: { color: color, width: 6 },
            name: name
        };
    } else if (obj.type === 'plane') {
        // Create plane mesh
        const range = 5;
        const step = 0.5;
        const x = [], y = [], z = [];
        
        for (let i = -range; i <= range; i += step) {
            for (let j = -range; j <= range; j += step) {
                x.push(i);
                y.push(j);
                // ax + by + cz + d = 0 => z = -(ax + by + d) / c
                if (obj.c !== 0) {
                    z.push(-(obj.a * i + obj.b * j + obj.d) / obj.c);
                } else {
                    z.push(0);
                }
            }
        }
        
        return {
            x: x, y: y, z: z,
            mode: 'markers',
            type: 'scatter3d',
            marker: { size: 2, color: color, opacity: 0.6 },
            name: `${name} (${obj.a}x + ${obj.b}y + ${obj.c}z + ${obj.d} = 0)`
        };
    } else if (obj.type === 'sphere') {
        // Create sphere surface
        const phi = Array.from({length: 20}, (_, i) => i * Math.PI / 19);
        const theta = Array.from({length: 20}, (_, i) => i * 2 * Math.PI / 19);
        
        const x = [], y = [], z = [];
        phi.forEach(p => {
            theta.forEach(t => {
                x.push(obj.center.x + obj.radius * Math.sin(p) * Math.cos(t));
                y.push(obj.center.y + obj.radius * Math.sin(p) * Math.sin(t));
                z.push(obj.center.z + obj.radius * Math.cos(p));
            });
        });
        
        return {
            x: x, y: y, z: z,
            mode: 'markers',
            type: 'scatter3d',
            marker: { size: 3, color: color, opacity: 0.8 },
            name: `${name} (r=${obj.radius})`
        };
    }
    
    return null;
}

function createOperationTrace2D(objA, objB, operation) {
    if (operation === 'Khoảng cách' && objA.type === 'point' && objB.type === 'point') {
        return {
            x: [objA.x, objB.x],
            y: [objA.y, objB.y],
            mode: 'lines',
            type: 'scatter',
            line: { color: '#4CAF50', width: 2, dash: 'dash' },
            name: 'Distance Line',
            hovertemplate: 'Distance connection<extra></extra>'
        };
    }
    return null;
}

function createOperationTrace3D(objA, objB, operation) {
    if (operation === 'Khoảng cách' && objA.type === 'point' && objB.type === 'point') {
        return {
            x: [objA.x, objB.x],
            y: [objA.y, objB.y],
            z: [objA.z || 0, objB.z || 0],
            mode: 'lines',
            type: 'scatter3d',
            line: { color: '#4CAF50', width: 6 },
            name: 'Distance Line'
        };
    }
    return null;
}

function resetView() {
    if (!plotInitialized) return;
    Plotly.relayout('geometryPlot', {
        'xaxis.autorange': true,
        'yaxis.autorange': true,
        'scene.camera': {
            eye: { x: 1.25, y: 1.25, z: 1.25 }
        }
    });
}

function toggle3D() {
    currentView = currentView === '2D' ? '3D' : '2D';
    updateVisualization();
}