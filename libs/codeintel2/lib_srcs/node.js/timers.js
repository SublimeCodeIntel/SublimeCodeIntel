/**
 * To schedule execution of callback after delay milliseconds. Returns a
 * timeoutId for possible use with clearTimeout(). Optionally, you can also
 * pass arguments to the callback.
 */
var timers = {};

/**
 * To schedule the repeated execution of callback every delay milliseconds.
 * Returns a intervalId for possible use with clearInterval(). Optionally,
 * you can also pass arguments to the callback.
 */
timers.setInterval = function() {}

/**
 * To schedule execution of callback after delay milliseconds. Returns a
 * timeoutId for possible use with clearTimeout(). Optionally, you can also
 * pass arguments to the callback.
 */
timers.setTimeout = function() {}

/**
 * Prevents a timeout from triggering.
 */
timers.clearTimeout = function() {}

/**
 * Stops a interval from triggering.
 */
timers.clearInterval = function() {}


exports = timers;

