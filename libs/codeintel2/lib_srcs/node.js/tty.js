/**
 * Use require('tty') to access this module.
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
 * mode should be true or false. This sets the properties of the current
 * process's stdin fd to act either as a raw device or default.
 * @param mode
 */
tty.setRawMode = function(mode) {}

exports = tty;

