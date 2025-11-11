// Lightweight expression parser to handle LaTeX inputs for visualization
// Supports: nested fractions, sqrt, trig functions, constants, basic operators
// Primary use: Parse LaTeX coordinate input → numeric values for Plotly.js

/**
 * Parse LaTeX expression to numeric value
 * Handles nested structures like \frac{\sqrt{7}}{8}
 * @param {string} expr - LaTeX or math expression
 * @returns {number} - Parsed numeric value or NaN
 */
function evalExpr(expr) {
  if (expr === undefined || expr === null) return NaN;
  if (typeof expr !== 'string') return Number(expr);
  
  let s = expr.trim();
  if (!s) return NaN;
  
  // Process complex nested LaTeX structures FIRST (order matters!)
  // 1. Nested: \frac{\sqrt{a}}{b} => Math.sqrt(a)/b
  s = s.replace(/\\frac\{\\sqrt\{([^{}]+)\}\}\{([^{}]+)\}/g, 'Math.sqrt($1)/($2)');
  
  // 2. Nested: \frac{a}{\sqrt{b}} => a/Math.sqrt(b)
  s = s.replace(/\\frac\{([^{}]+)\}\{\\sqrt\{([^{}]+)\}\}/g, '($1)/Math.sqrt($2)');
  
  // 3. Nested: \frac{\sqrt{a}}{\sqrt{b}} => Math.sqrt(a)/Math.sqrt(b)
  s = s.replace(/\\frac\{\\sqrt\{([^{}]+)\}\}\{\\sqrt\{([^{}]+)\}\}/g, 'Math.sqrt($1)/Math.sqrt($2)');
  
  // 4. Nested: \sqrt{\sqrt{x}} => Math.sqrt(Math.sqrt(x))
  s = s.replace(/\\sqrt\{\\sqrt\{([^{}]+)\}\}/g, 'Math.sqrt(Math.sqrt($1))');
  
  // 5. Nested: \sqrt{\frac{a}{b}} => Math.sqrt(a/b)
  s = s.replace(/\\sqrt\{\\frac\{([^{}]+)\}\{([^{}]+)\}\}/g, 'Math.sqrt(($1)/($2))');
  
  // 6. Basic: \frac{a}{b} => a/b
  s = s.replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g, '($1)/($2)');
  
  // 7. Basic: \sqrt{x} => Math.sqrt(x)
  s = s.replace(/\\sqrt\{([^{}]+)\}/g, 'Math.sqrt($1)');
  
  // 8. Alternative: sqrt(x) without backslash
  s = s.replace(/\\?sqrt\s*\(([^()]*)\)/g, 'Math.sqrt($1)');
  
  // 9. Trigonometric functions
  s = s.replace(/\\sin\s*\(/g, 'Math.sin(');
  s = s.replace(/\bsin\s*\(/g, 'Math.sin(');
  s = s.replace(/\\cos\s*\(/g, 'Math.cos(');
  s = s.replace(/\bcos\s*\(/g, 'Math.cos(');
  s = s.replace(/\\tan\s*\(/g, 'Math.tan(');
  s = s.replace(/\btan\s*\(/g, 'Math.tan(');
  
  // 10. Logarithmic functions
  s = s.replace(/\\ln\s*\(/g, 'Math.log(');
  s = s.replace(/\bln\s*\(/g, 'Math.log(');
  s = s.replace(/\\log\s*\(/g, 'Math.log10(');
  s = s.replace(/\blog\s*\(/g, 'Math.log10(');
  
  // 11. Constants
  s = s.replace(/\\pi\b|\bpi\b/gi, 'Math.PI');
  s = s.replace(/\\e\b/g, 'Math.E');
  
  // 12. Exponential
  s = s.replace(/\\?exp\s*\(([^()]*)\)/g, 'Math.exp($1)');
  
  // 13. Power operator
  s = s.replace(/\^/g, '**');
  
  // 14. Clean up remaining braces (convert to parentheses)
  s = s.replace(/\{/g, '(').replace(/\}/g, ')');
  
  try {
    // Use Function constructor (safer than eval for expressions)
    // eslint-disable-next-line no-new-func
    const val = Function('return (' + s + ')')();
    const num = Number(val);
    return isNaN(num) ? NaN : num;
  } catch (e) {
    console.warn('evalExpr parse error:', expr, '→', s, e);
    return NaN;
  }
}

/**
 * Parse comma-separated list of expressions
 * Example: "\\frac{\\sqrt{7}}{8}, 1, 2" → [0.33, 1, 2]
 * @param {string} str - Comma-separated coordinate string
 * @returns {number[]} - Array of parsed numeric values
 */
function parseNumberList(str) {
  if (!str || typeof str !== 'string') return [];
  return str.split(',').map(t => evalExpr(t)).filter(v => !isNaN(v));
}

// Export to global scope for use in other modules
window.evalExpr = evalExpr;
window.parseNumberList = parseNumberList;
