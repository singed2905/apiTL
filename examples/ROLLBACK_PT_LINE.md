# Rollback plan for PT đường thẳng feature

This commit reverts the recent visualization and manual line equation changes to the state at commit 5a5f033.

Steps executed:
- Revert changes in examples/index.html related to added scripts (visualization_global_shim.js, visualization_expose_update.js, visualization_safe_patch.js, line_equation_manual.js)
- Restore visualization.js to the state before drawing 'PT đường thẳng' operation
- Keep earlier commits unrelated to this feature intact (chunked processing, modularization)

If needed, cherry-pick specific files from 5a5f033 parent.
