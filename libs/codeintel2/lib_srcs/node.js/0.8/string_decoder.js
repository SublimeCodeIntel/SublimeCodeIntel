/**
 * To use this module, do require('string_decoder'). StringDecoder decodes
 * a buffer to a string. It is a simple interface to buffer.toString() but
 * provides additional support for utf8.
 */
var string_decoder = {};

/**
 * Accepts a single argument, encoding which defaults to utf8.
 * @constructor
 */
string_decoder.StringDecoder = function() {}

/**
 * Returns a decoded string.
 * @param buffer
 * @returns a decoded string
 */
string_decoder.StringDecoder.prototype.write = function(buffer) {}

exports = string_decoder;

