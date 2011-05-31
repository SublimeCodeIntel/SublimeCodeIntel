/**
 * This module contains utilities for dealing with file paths. Use
 * require('path') to use it. It provides the following methods:
 */
var path = {};

/**
 * Normalize a string path, taking care of '..' and '.' parts.
 */
path.normalize = function() {}

/**
 * Resolves to to an absolute path.
 */
path.resolve = function() {}

/**
 * Join all arguments together and normalize the resulting path.
 */
path.join = function() {}

/**
 * Test whether or not the given path exists. Then, call the callback
 * argument with either true or false. Example:
 */
path.exists = function() {}

/**
 * Return the last portion of a path. Similar to the Unix basename command.
 */
path.basename = function() {}

/**
 * Return the extension of the path. Everything after the last '.' in the
 * last portion of the path. If there is no '.' in the last portion of the
 * path or the only '.' is the first character, then it returns an empty
 * string. Examples:
 */
path.extname = function() {}

/**
 * Synchronous version of path.exists.
 */
path.existsSync = function() {}

/**
 * Return the directory name of a path. Similar to the Unix dirname
 * command.
 */
path.dirname = function() {}


exports = path;

