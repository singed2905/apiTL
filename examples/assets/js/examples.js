const examples = {
    distance_points: {
        operation: 'Khoảng cách',
        shapeA: 'Điểm',
        shapeB: 'Điểm',
        dataA: { point_input: '1,2,3' },
        dataB: { point_input: '4,5,6' }
    },
    circle_area: {
        operation: 'Diện tích',
        shapeA: 'Đường tròn',
        dataA: {
            circle_center: '0,0',
            circle_radius: 'sqrt(5)'
        }
    },
    sphere_volume: {
        operation: 'Thể tích',
        shapeA: 'Mặt cầu',
        dataA: {
            sphere_center: '0,0,0',
            sphere_radius: '3'
        }
    },
    line_plane_intersection: {
        operation: 'Tương giao',
        shapeA: 'Đường thẳng',
        shapeB: 'Mặt phẳng',
        dataA: {
            line_A1: '0,0,0',
            line_X1: '1,1,1'
        },
        dataB: {
            plane_a: '1',
            plane_b: '1',
            plane_c: '1',
            plane_d: '0'
        }
    }
};

function loadExample(key) {
    const example = examples[key];
    if (!example) {
        console.error('Example not found:', key);
        return;
    }
    
    // Set operation
    document.getElementById('operation').value = example.operation;
    
    // Update shapes first
    updateShapeOptions().then(() => {
        // Set shapes
        document.getElementById('shapeA').value = example.shapeA;
        if (example.shapeB) {
            document.getElementById('shapeB').value = example.shapeB;
        }
        
        // Update input fields
        updateInputFields();
        
        // Fill in data after inputs are created
        setTimeout(() => {
            // Fill Shape A data
            Object.entries(example.dataA).forEach(([key, value]) => {
                const input = document.getElementById(`${key}_A`);
                if (input) {
                    input.value = value;
                }
            });
            
            // Fill Shape B data if exists
            if (example.dataB) {
                Object.entries(example.dataB).forEach(([key, value]) => {
                    const input = document.getElementById(`${key}_B`);
                    if (input) {
                        input.value = value;
                    }
                });
            }
            
            // Update visualization
            updateVisualization();
        }, 100);
    }).catch(error => {
        console.error('Error loading example:', error);
    });
}