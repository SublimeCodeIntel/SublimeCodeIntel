/**
 * This module contains utilities for handling and transforming file paths.
 * Almost all these methods perform only string transformations.
 */
var path = {};

/**
 * Normalize a string path, taking care of '..' and '.' parts.
 * @param p
 */
path.normalize = function(p) {}

/**
 * Resolves to to an absolute path.
 * @param from 
 * @param to
 */
path.resolve = function(from , to) {}

/**
 * Join all arguments together and normalize the resulting path.
 * @param path1
 * @param path2
 */
path.join = function(path1, path2) {}

/**
 * Test whether or not the given path exists by checking with the file
 * system.
 * @param p
 * @param callback
 */
path.exists = function(p, callback) {}

/**
 * Return the last portion of a path. Similar to the Unix basename command.
 * @param p
 * @param ext
 */
path.basename = function(p, ext) {}

/**
 * Return the extension of the path, from the last '.' to end of string in
 * the last portion of the path. If there is no '.' in the last portion of
 * the path or the first character of it is '.', then it returns an empty
 * string. Examples:
 * @param p
 */
path.extname = function(p) {}

/**
 * Synchronous version of path.exists.
 * @param p
 */
path.existsSync = function(p) {}

/**
 * Return the directory name of a path. Similar to the Unix dirname
 * command.
 * @param p
 */
path.dirname = function(p) {}

/**
 * Solve the relative path from from to to.
 * @param from
 * @param to
 */
path.relative = function(from, to) {}

exports = path;

