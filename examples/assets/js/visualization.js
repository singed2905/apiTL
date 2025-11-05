function createOperationTrace2D(objA, objB, operation) {
    // Draw helper for infinite-looking line through two points
    function lineThroughPointsTrace2D(p1, p2, color) {
        const dx = p2.x - p1.x;
        const dy = p2.y - p1.y;
        if (dx === 0 && dy === 0) return null; // identical points
        // Build long segment around the two points so it looks like a full line
        const scale = 1000; // large factor to extend
        const xa = p1.x - dx * scale;
        const ya = p1.y - dy * scale;
        const xb = p1.x + dx * scale;
        const yb = p1.y + dy * scale;
        return {
            x: [xa, xb],
            y: [ya, yb],
            mode: 'lines',
            type: 'scatter',
            line: { color: color || '#4CAF50', width: 2 },
            name: 'Đường thẳng qua A, B',
            hovertemplate: 'Line through A & B<extra></extra>'
        };
    }

    if (!objA || !objB) return null;

    if (operation === 'Khoảng cách') {
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

    if (operation === 'Phương trình đường thẳng' || operation === 'PT đường thẳng') {
        // Draw full line through two points
        return lineThroughPointsTrace2D(objA, objB, '#4CAF50');
    }

    return null;
}
