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

  // 1. Nested frac with sqrt numerator
  s = s.replace(/\\frac{\\sqrt{([^{}]+)}}{([^{}]+)}/g, '(Math.sqrt($1))/($2)');

  // 2. Nested frac with sqrt denominator
  s = s.replace(/\\frac{([^{}]+)}{\\sqrt{([^{}]+)}}/g, '($1)/(Math.sqrt($2))');

  // 3. Nested frac with sqrt in both
  s = s.replace(/\\frac{\\sqrt{([^{}]+)}}{\\sqrt{([^{}]+)}}/g, '(Math.sqrt($1))/(Math.sqrt($2))');

  // 4. sqrt of sqrt
  s = s.replace(/\\sqrt{\\sqrt{([^{}]+)}}/g, 'Math.sqrt(Math.sqrt($1))');

  // 5. sqrt of frac
  s = s.replace(/\\sqrt{\\frac{([^{}]+)}{([^{}]+)}}/g, 'Math.sqrt(($1)/($2))');

  // 6. Basic frac
  s = s.replace(/\\frac{([^{}]+)}{([^{}]+)}/g, '($1)/($2)');

  // 7. Replace only \sqrt{...}
  s = s.replace(/\\sqrt{([^{}]+)}/g, function (_, inner) {
    return 'Math.sqrt(' + inner + ')';
  });

  // 8. sqrt(x) dạng ascii
  s = s.replace(/sqrt\(([^()]*)\)/g, function (_, inner) {
    return 'Math.sqrt(' + inner + ')';
  });

  // 9. Trig, log/cos/tan, pi, e, exp gần như cũ
  s = s.replace(/\\sin\s*\(/g, 'Math.sin(');
  s = s.replace(/\bsin\s*\(/g, 'Math.sin(');
  s = s.replace(/\\cos\s*\(/g, 'Math.cos(');
  s = s.replace(/\bcos\s*\(/g, 'Math.cos(');
  s = s.replace(/\\tan\s*\(/g, 'Math.tan(');
  s = s.replace(/\btan\s*\(/g, 'Math.tan(');
  s = s.replace(/\\ln\s*\(/g, 'Math.log(');
  s = s.replace(/\bln\s*\(/g, 'Math.log(');
  s = s.replace(/\\log\s*\(/g, 'Math.log10(');
  s = s.replace(/\blog\s*\(/g, 'Math.log10(');
  s = s.replace(/\\pi\b|\bpi\b/gi, 'Math.PI');
  s = s.replace(/\\e\b/g, 'Math.E');
  s = s.replace(/\\?exp\s*\(([^()]*)\)/g, 'Math.exp($1)');
  s = s.replace(/\^/g, '**');
  s = s.replace(/{/g, '(').replace(/}/g, ')');

  try {
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
