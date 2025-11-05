// Delay exposing until functions are defined
(function(){
  function expose(){
    if (typeof handleExcelLocal === 'function') window.handleExcelLocal = handleExcelLocal;
    if (typeof processBatchChunked === 'function') window.processBatchChunked = processBatchChunked;
    if (typeof populateBatchConfig === 'function') window.populateBatchConfig = populateBatchConfig;
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', expose);
  } else {
    expose();
  }
})();
