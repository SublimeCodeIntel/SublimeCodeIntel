/**
 * To use this module, do require('readline'). Readline allows reading of a
 * stream (such as STDIN) on a line-by-line basis.
 */
var readline = {};

/**
 * Takes two streams and creates a readline interface. The completer
 * function is used for autocompletion. When given a substring, it returns
 * [[substr1, substr2, ...], originalsubstring].
 * @param input
 * @param output
 * @param completer
 * @returns {readline.Interface}
 */
readline.createInterface = function(input, output, completer) {}

/**
 * The class that represents a readline interface with a stdin and stdout
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
 * options on a new line, giving the user a new spot to write.
 */
readline.Interface.prototype.prompt = function() {}

/**
 * Prepends the prompt with query and invokes callback with the user's
 * response. Displays the query to the user, and then invokes callback with
 * the user's response after it has been typed.
 * @param query
 * @param callback
 */
readline.Interface.prototype.question = function(query, callback) {}

/**
 *  Closes tty.
 */
readline.Interface.prototype.close = function() {}

/**
 *  Pauses tty.
 */
readline.Interface.prototype.pause = function() {}

/**
 *  Resumes tty.
 */
readline.Interface.prototype.resume = function() {}

/**
 *  Writes to tty.
 */
readline.Interface.prototype.write = function() {}

/** @__local__ */ readline.Interface.__events__ = {};

/**
 * Emitted whenever the in stream receives a \n, usually received when the
 * user hits enter, or return. This is a good hook to listen for user
 * input. Example of listening for line:
 * @param line {String}
 */
readline.Interface.__events__.line = function(line) {};

/**
 * Emitted whenever the in stream receives a ^C or ^D, respectively known
 * as SIGINT and EOT. This is a good way to know the user is finished using
 * your program. Example of listening for close, and exiting the program
 * afterward: Here's an example of how to use all these together to craft a
 * tiny command line interface: Take a look at this slightly more
 * complicated example, and http-console for a real-life use case.
 */
readline.Interface.__events__.close = function() {};

var events = require('events');

exports = readline;

