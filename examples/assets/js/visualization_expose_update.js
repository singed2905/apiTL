// Ensure updateVisualization is globally accessible before examples.js/app.js call it
(function ensureUpdateVisualizationGlobal(){
  if (typeof window.updateVisualization !== 'function' && typeof updateVisualization === 'function') {
    window.updateVisualization = updateVisualization;
  }
})();
