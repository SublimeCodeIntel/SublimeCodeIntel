/**
 * All of the timer functions are globals. You do not need to require()
 * this module in order to use them.
 */
var timers = {};

/**
 * To schedule the repeated execution of callback every delay milliseconds.
 * @param callback
 * @param delay
 * @param arg
 */
timers.setInterval = function(callback, delay, arg) {}

/**
 * To schedule execution of a one-time callback after delay milliseconds.
 * Returns a timeoutId for possible use with clearTimeout(). Optionally you
 * can also pass arguments to the callback.
 * @param callback
 * @param delay
 * @param arg
 * @returns a timeoutId for possible use with clearTimeout()
 */
timers.setTimeout = function(callback, delay, arg) {}

/**
 * Prevents a timeout from triggering.
 * @param timeoutId
 */
timers.clearTimeout = function(timeoutId) {}

/**
 * Stops a interval from triggering.
 * @param intervalId
 */
timers.clearInterval = function(intervalId) {}

exports = timers;

