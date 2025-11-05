// Guarded call to updateVisualization to avoid ReferenceError during early init
function safeUpdateVisualization(){
  if (typeof window.updateVisualization === 'function') {
    try { window.updateVisualization(); } catch (e) { console.error('updateVisualization failed:', e); }
  }
}

// Patch app.js hooks by redefining updateInputFields to call safe function
(function patchAppUpdateInputFields(){
  if (typeof updateInputFields === 'function') {
    const original = updateInputFields;
    window.updateInputFields = function(){
      try { original.apply(this, arguments); } finally { safeUpdateVisualization(); }
    }
  }
})();
