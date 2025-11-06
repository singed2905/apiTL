// Lightweight expression parser to handle simple LaTeX-like inputs
// Supported: sqrt(x), pi, e, fractions like a/b, basic + - * / ^, parentheses
// Also supports vectors/points entered as "1, sqrt(5), 3/2"

function evalExpr(expr){
  if(expr===undefined || expr===null) return NaN;
  if(typeof expr!=='string') return Number(expr);
  let s = expr.trim();
  if(!s) return NaN;
  // Normalize commas inside numbers won't be used; keep commas for coordinate split at higher level
  // Replace LaTeX-like tokens
  s = s.replace(/\\?sqrt\s*\(([^()]*)\)/g, 'Math.sqrt($1)');
  s = s.replace(/\\pi\b|\bpi\b/gi, 'Math.PI');
  s = s.replace(/\\?exp\s*\(([^()]*)\)/g, 'Math.exp($1)');
  s = s.replace(/\^/g, '**');
  // Simple fraction a/b when no parentheses around (avoid replacing URLs etc.)
  // Leave it to JS operator since we use ** and normal / operators
  try{
    // eslint-disable-next-line no-new-func
    const val = Function('return ('+s+')')();
    const num = Number(val);
    return isNaN(num) ? NaN : num;
  }catch(e){
    return NaN;
  }
}

function parseNumberList(str){
  if(!str || typeof str!=='string') return [];
  return str.split(',').map(t=>evalExpr(t)).filter(v=>!isNaN(v));
}

window.evalExpr = evalExpr;
window.parseNumberList = parseNumberList;
