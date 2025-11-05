function parseCurrentGeometry() {
    const shapeA = document.getElementById('shapeA').value;
    const shapeB = document.getElementById('shapeB').value;
    
    return {
        objA: parseShape('A', shapeA),
        objB: parseShape('B', shapeB)
    };
}

function parseShape(group, shape) {
    if (!shape) return null;
    
    const data = collectInputData(group, shape);
    
    if (shape === 'Điểm') {
        return parsePoint(data.point_input);
    } else if (shape === 'Đường thẳng') {
        const pointKey = `line_A${group === 'A' ? '1' : '2'}`;
        const vectorKey = `line_X${group === 'A' ? '1' : '2'}`;
        return parseLine(data[pointKey], data[vectorKey]);
    } else if (shape === 'Mặt phẳng') {
        return parsePlane(data.plane_a, data.plane_b, data.plane_c, data.plane_d);
    } else if (shape === 'Đường tròn') {
        return parseCircle(data.circle_center, data.circle_radius);
    } else if (shape === 'Mặt cầu') {
        return parseSphere(data.sphere_center, data.sphere_radius);
    }
    
    return null;
}

function parsePoint(input) {
    if (!input || input.trim() === '') return null;
    
    const coords = input.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
    if (coords.length < 2) return null;
    
    return {
        type: 'point',
        x: coords[0],
        y: coords[1],
        z: coords[2] || 0
    };
}

function parseLine(pointInput, vectorInput) {
    if (!pointInput || !vectorInput || pointInput.trim() === '' || vectorInput.trim() === '') return null;
    
    const point = pointInput.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
    const vector = vectorInput.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
    
    if (point.length < 2 || vector.length < 2) return null;
    
    const is3D = point.length >= 3 || vector.length >= 3 || (point[2] && point[2] !== 0) || (vector[2] && vector[2] !== 0);
    
    return {
        type: is3D ? 'line3d' : 'line',
        point: {
            x: point[0],
            y: point[1],
            z: point[2] || 0
        },
        vector: {
            x: vector[0],
            y: vector[1],
            z: vector[2] || 0
        }
    };
}

function parsePlane(a, b, c, d) {
    const coeffs = [a, b, c, d].map(s => {
        if (!s || s.trim() === '') return NaN;
        return parseFloat(s.trim());
    });
    
    if (coeffs.some(n => isNaN(n))) return null;
    if (coeffs[0] === 0 && coeffs[1] === 0 && coeffs[2] === 0) return null; // Invalid plane
    
    return {
        type: 'plane',
        a: coeffs[0],
        b: coeffs[1],
        c: coeffs[2],
        d: coeffs[3]
    };
}

function parseCircle(centerInput, radiusInput) {
    if (!centerInput || !radiusInput || centerInput.trim() === '' || radiusInput.trim() === '') return null;
    
    const center = centerInput.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
    const radius = parseFloat(radiusInput.trim());
    
    if (center.length < 2 || isNaN(radius) || radius <= 0) return null;
    
    return {
        type: 'circle',
        center: {
            x: center[0],
            y: center[1]
        },
        radius: radius
    };
}

function parseSphere(centerInput, radiusInput) {
    if (!centerInput || !radiusInput || centerInput.trim() === '' || radiusInput.trim() === '') return null;
    
    const center = centerInput.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
    const radius = parseFloat(radiusInput.trim());
    
    if (center.length < 3 || isNaN(radius) || radius <= 0) return null;
    
    return {
        type: 'sphere',
        center: {
            x: center[0],
            y: center[1],
            z: center[2]
        },
        radius: radius
    };
}

// Utility functions for geometry calculations
function calculateDistance(pointA, pointB) {
    const dx = pointB.x - pointA.x;
    const dy = pointB.y - pointA.y;
    const dz = (pointB.z || 0) - (pointA.z || 0);
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
}

function calculateCircleArea(circle) {
    return Math.PI * circle.radius * circle.radius;
}

function calculateSphereVolume(sphere) {
    return (4 / 3) * Math.PI * Math.pow(sphere.radius, 3);
}

// Shape validation helpers
function validateShapeData(shape, data) {
    if (!shape || !data) return false;
    
    switch (shape) {
        case 'Điểm':
            return data.point_input && data.point_input.trim() !== '';
        case 'Đường thẳng':
            const hasPoint = data.line_A1 || data.line_A2;
            const hasVector = data.line_X1 || data.line_X2;
            return hasPoint && hasVector;
        case 'Mặt phẳng':
            return data.plane_a && data.plane_b && data.plane_c && data.plane_d;
        case 'Đường tròn':
            return data.circle_center && data.circle_radius;
        case 'Mặt cầu':
            return data.sphere_center && data.sphere_radius;
        default:
            return false;
    }
}

function getShapeDescription(obj) {
    if (!obj) return 'Empty';
    
    switch (obj.type) {
        case 'point':
            return `Point (${obj.x}, ${obj.y}${obj.z !== 0 ? ', ' + obj.z : ''})`;
        case 'line':
        case 'line3d':
            return `Line through (${obj.point.x}, ${obj.point.y}${obj.point.z !== 0 ? ', ' + obj.point.z : ''}) with direction (${obj.vector.x}, ${obj.vector.y}${obj.vector.z !== 0 ? ', ' + obj.vector.z : ''})`;
        case 'plane':
            return `Plane: ${obj.a}x + ${obj.b}y + ${obj.c}z + ${obj.d} = 0`;
        case 'circle':
            return `Circle centered at (${obj.center.x}, ${obj.center.y}) with radius ${obj.radius}`;
        case 'sphere':
            return `Sphere centered at (${obj.center.x}, ${obj.center.y}, ${obj.center.z}) with radius ${obj.radius}`;
        default:
            return 'Unknown shape';
    }
}

// Mathematical helper functions
function evaluateExpression(expr) {
    // Basic expression evaluator for simple math like "sqrt(5)"
    if (!expr || typeof expr !== 'string') return NaN;
    
    // Replace common functions
    let cleanExpr = expr.replace(/sqrt\((.*?)\)/g, 'Math.sqrt($1)');
    cleanExpr = cleanExpr.replace(/pi/gi, 'Math.PI');
    cleanExpr = cleanExpr.replace(/e/gi, 'Math.E');
    
    try {
        // Security note: In production, use a proper expression parser
        return Function('"use strict"; return (' + cleanExpr + ')')();
    } catch (e) {
        return parseFloat(expr);
    }
}