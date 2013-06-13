
/**
 * For printing to stdout and stderr. Similar to the console object
 * functions provided by most web browsers, here the output is sent to
 * stdout or stderr.
 * @type {Object}
 */
var console = {};

/**
 * Same as console.log.
 * @param data
 */
console.info = function(data) {}

/**
 * Same as [assert.ok()][] where if the expression evaluates as false throw
 * an AssertionError with message.
 * @param expression
 * @param message
 */
console.assert = function(expression, message) {}

/**
 * Prints to stdout with newline. This function can take multiple arguments
 * in a printf()-like way. Example:
 * @param data
 */
console.log = function(data) {}

/**
 * Print a stack trace to stderr of the current position.
 * @param label
 */
console.trace = function(label) {}

/**
 * Same as console.log but prints to stderr.
 * @param data
 */
console.error = function(data) {}

/**
 * Finish timer, record output. Example:
 * @param label
 */
console.timeEnd = function(label) {}

/**
 * Same as console.error.
 * @param data
 */
console.warn = function(data) {}

/**
 * Mark a time.
 * @param label
 */
console.time = function(label) {}

/**
 * Uses util.inspect on obj and prints resulting string to stdout.
 * @param obj
 */
console.dir = function(obj) {}

exports = console;

