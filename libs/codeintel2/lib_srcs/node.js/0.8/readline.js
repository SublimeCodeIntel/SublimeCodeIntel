/**
 * To use this module, do require('readline'). Readline allows reading of a
 * stream (such as process.stdin) on a line-by-line basis.
 */
var readline = {};

/**
 * Creates a readline Interface instance. Accepts an "options" Object that
 * takes the following values:
 * @param options
 * @returns {readline.Interface}
 */
readline.createInterface = function(options) {}

/**
 * The class that represents a readline interface with an input and output
 * stream.
 * @constructor
 */
readline.Interface = function() {}
readline.Interface.prototype = new events.EventEmitter();

/**
 * Sets the prompt, for example when you run node on the command line, you
 * see &gt; , which is node's prompt.
 * @param prompt
 * @param length
 */
readline.Interface.prototype.setPrompt = function(prompt, length) {}

/**
 * Readies readline for input from the user, putting the current setPrompt
 * options on a new line, giving the user a new spot to write. Set
 * preserveCursor to true to prevent the cursor placement being reset to 0.
 * @param preserveCursor
 */
readline.Interface.prototype.prompt = function(preserveCursor) {}

/**
 * Prepends the prompt with query and invokes callback with the user's
 * response. Displays the query to the user, and then invokes callback with
 * the user's response after it has been typed.
 * @param query
 * @param callback
 */
readline.Interface.prototype.question = function(query, callback) {}

/**
 * Pauses the readline input stream, allowing it to be resumed later if
 * needed.
 */
readline.Interface.prototype.pause = function() {}

/**
 * Resumes the readline input stream.
 */
readline.Interface.prototype.resume = function() {}

/**
 * Closes the Interface instance, relinquishing control on the input and
 * output streams. The "close" event will also be emitted.
 */
readline.Interface.prototype.close = function() {}

/**
 * Writes data to output stream. key is an object literal to represent a
 * key sequence; available if the terminal is a TTY.
 * @param data
 * @param key
 */
readline.Interface.prototype.write = function(data, key) {}

var events = require('events');

exports = readline;

