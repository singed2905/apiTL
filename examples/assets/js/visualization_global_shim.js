// Ensure functions are globally available when included before app.js
window.setupVisualizationListeners = window.setupVisualizationListeners || function(){ console.log('setupVisualizationListeners not yet defined'); };
window.initializeVisualization = window.initializeVisualization || function(){ console.log('initializeVisualization not yet defined'); };

// Move actual implementations onto window after script load
(function exposeVisualizationGlobals(){
    if (typeof setupVisualizationListeners === 'function') {
        window.setupVisualizationListeners = setupVisualizationListeners;
    }
    if (typeof initializeVisualization === 'function') {
        window.initializeVisualization = initializeVisualization;
    }
    if (typeof updateVisualization === 'function') {
        window.updateVisualization = updateVisualization;
    }
})();
