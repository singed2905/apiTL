function getFirstAvailable(row, keys){
  for(const k of keys){
    if(Object.prototype.hasOwnProperty.call(row,k) && row[k]!==undefined && row[k]!==null && row[k]!=='' ){
      return row[k];
    }
  }
  return undefined;
}
window.getFirstAvailable = getFirstAvailable;
