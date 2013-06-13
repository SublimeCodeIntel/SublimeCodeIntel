/**
 * The tty module houses the tty.ReadStream and tty.WriteStream classes. In
 * most cases, you will not need to use this module directly.
 */
var tty = {};

/**
 * Returns true or false depending on if the fd is associated with a
 * terminal.
 * @param fd
 * @returns true or false depending on if the fd is associated with a terminal
 */
tty.isatty = function(fd) {}

/**
 * Deprecated. Use tty.ReadStream#setRawMode() (i.e.
 * process.stdin.setRawMode()) instead.
 * @param mode
 */
tty.setRawMode = function(mode) {}

/**
 * A net.Socket subclass that represents the readable portion of a tty. In
 * normal circumstances, process.stdin will be the only tty.ReadStream
 * instance in any node program (only when isatty(0) is true).
 * @constructor
 */
tty.ReadStream = function() {}
tty.ReadStream.prototype = new net.Socket();

/**
 * mode should be true or false. This sets the properties of the
 * tty.ReadStream to act either as a raw device or default. isRaw will be
 * set to the resulting mode.
 * @param mode
 */
tty.ReadStream.prototype.setRawMode = function(mode) {}

/**
 * A Boolean that is initialized to false. It represents the current "raw"
 * state of the tty.ReadStream instance.
 * @type {Boolean}
 */
tty.ReadStream.prototype.isRaw = 0;

/**
 * A net.Socket subclass that represents the writable portion of a tty. In
 * normal circumstances, process.stdout will be the only tty.WriteStream
 * instance ever created (and only when isatty(1) is true).
 * @constructor
 */
tty.WriteStream = function() {}
tty.WriteStream.prototype = new net.Socket();

/**
 * A Number that gives the number of columns the TTY currently has. This
 * property gets updated on "resize" events.
 * @type {Number}
 */
tty.WriteStream.prototype.columns = 0;

/**
 * A Number that gives the number of rows the TTY currently has. This
 * property gets updated on "resize" events.
 * @type {Number}
 */
tty.WriteStream.prototype.rows = 0;

/** @__local__ */ tty.WriteStream.__events__ = {};

/**
 * Emitted by refreshSize() when either of the columns or rows properties
 * has changed.
 */
tty.WriteStream.__events__.resize = function() {};

{} // workaround for bug 94560
net = require('net');

exports = tty;

