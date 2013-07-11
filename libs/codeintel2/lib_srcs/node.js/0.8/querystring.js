/**
 * This module provides utilities for dealing with query strings.
 */
var querystring = {};

/**
 * Deserialize a query string to an object.
 * @param str
 * @param sep
 * @param eq
 * @param options
 */
querystring.parse = function(str, sep, eq, options) {}

/**
 * Serialize an object to a query string.
 * @param obj
 * @param sep
 * @param eq
 */
querystring.stringify = function(obj, sep, eq) {}

/**
 * The unescape function used by querystring.parse, provided so that it
 * could be overridden if necessary.
 */
querystring.unescape = function() {}

/**
 * The escape function used by querystring.stringify, provided so that it
 * could be overridden if necessary.
 */
querystring.escape = function() {}

exports = querystring;

