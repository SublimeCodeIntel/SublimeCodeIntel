/**
 * These functions are in the module 'util'. Use require('util') to access
 * them.
 */
var util = {};

/**
 * A synchronous output function. Will block the process and output string
 * immediately to stderr.
 * @param string
 */
util.debug = function(string) {}

/**
 * Inherit the prototype methods from one constructor into another. The
 * prototype of constructor will be set to a new object created from
 * superConstructor.
 * @param constructor
 * @param superConstructor
 */
util.inherits = function(constructor, superConstructor) {}

/**
 * Experimental
 * @param readableStream
 * @param writableStream
 * @param callback
 */
util.pump = function(readableStream, writableStream, callback) {}

/**
 * Return a string representation of object, which is useful for debugging.
 * @param object
 * @param showHidden
 * @param depth
 * @param colors
 */
util.inspect = function(object, showHidden, depth, colors) {}

/**
 * Output with timestamp on stdout.
 * @param string
 */
util.log = function(string) {}

/**
 * Returns a formatted string using the first argument as a printf-like
 * format.
 * @returns a formatted string using the first argument as a printf-like format
 */
util.format = function() {}

/**
 * Returns true if the given "object" is an Array. false otherwise.
 * @param object
 * @returns true if the given "object" is an Array
 */
util.isArray = function(object) {}

/**
 * Returns true if the given "object" is a Date. false otherwise.
 * @param object
 * @returns true if the given "object" is a Date
 */
util.isDate = function(object) {}

/**
 * Returns true if the given "object" is an Error. false otherwise.
 * @param object
 * @returns true if the given "object" is an Error
 */
util.isError = function(object) {}

/**
 * Returns true if the given "object" is a RegExp. false otherwise.
 * @param object
 * @returns true if the given "object" is a RegExp
 */
util.isRegExp = function(object) {}

exports = util;

