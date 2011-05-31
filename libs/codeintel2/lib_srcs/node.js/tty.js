/**
 * Use require('tty') to access this module.
 */
var tty = {};

/**
 * Returns true or false depending on if the fd is associated with a
 * terminal.
 */
tty.isatty = function() {}

/**
 * ioctls the window size settings to the file descriptor.
 */
tty.setWindowSize = function() {}

/**
 * Spawns a new process with the executable pointed to by path as the
 * session leader to a new pseudo terminal.
 * @returns child_process.ChildProcess
 */
tty.open = function() {}

/**
 * mode should be true or false. This sets the properties of the current
 * process's stdin fd to act either as a raw device or default.
 */
tty.setRawMode = function() {}

/**
 * Returns [row, col] for the TTY associated with the file descriptor.
 */
tty.getWindowSize = function() {}


                /* return value of tty.open */
                var child_process = require('child_process');
                exports = tty;

