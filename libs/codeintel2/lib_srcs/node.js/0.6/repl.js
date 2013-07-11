/**
 * A Read-Eval-Print-Loop (REPL) is available both as a standalone program
 * and easily includable in other programs. REPL provides a way to
 * interactively run JavaScript and see the results. It can be used for
 * debugging, testing, or just trying things out.
 */
var repl = {};

/**
 * Starts a REPL with prompt as the prompt and stream for all I/O. prompt
 * is optional and defaults to &gt; . stream is optional and defaults to
 * process.stdin. eval is optional too and defaults to async wrapper for
 * eval().
 * @param prompt
 * @param stream
 * @param eval
 * @param useGlobal
 * @param ignoreUndefined
 */
repl.start = function(prompt, stream, eval, useGlobal, ignoreUndefined) {}

exports = repl;

