/**
 * Domains provide a way to handle multiple different IO operations as a
 * single group. If any of the event emitters or callbacks registered to a
 * domain emit an error event, or throw an error, then the domain object
 * will be notified, rather than losing the context of the error in the
 * process.on('uncaughtException') handler, or causing the program to exit
 * with an error code.
 */
var domain = {};

/**
 * Returns a new Domain object.
 * @returns {domain.Domain} a new Domain object
 */
domain.create = function() {}

/**
 * The Domain class encapsulates the functionality of routing errors and
 * uncaught exceptions to the active Domain object.
 * @constructor
 */
domain.Domain = function() {}

/**
 * Run the supplied function in the context of the domain, implicitly
 * binding all event emitters, timers, and lowlevel requests that are
 * created in that context.
 * @param fn {Function}
 */
domain.Domain.prototype.run = function(fn) {}

/**
 * Explicitly adds an emitter to the domain. If any event handlers called
 * by the emitter throw an error, or if the emitter emits an error event,
 * it will be routed to the domain's error event, just like with implicit
 * binding.
 * @param emitter {EventEmitter | Timer}
 */
domain.Domain.prototype.add = function(emitter) {}

/**
 * The opposite of domain.add(emitter). Removes domain handling from the
 * specified emitter.
 * @param emitter {EventEmitter | Timer}
 */
domain.Domain.prototype.remove = function(emitter) {}

/**
 * The returned function will be a wrapper around the supplied callback
 * function. When the returned function is called, any errors that are
 * thrown will be routed to the domain's error event.
 * @param cb {Function}
 * @returns The bound function
 */
domain.Domain.prototype.bind = function(cb) {}

/**
 * This method is almost identical to domain.bind(cb). However, in addition
 * to catching thrown errors, it will also intercept Error objects sent as
 * the first argument to the function.
 * @param cb {Function}
 * @returns The intercepted function
 */
domain.Domain.prototype.intercept = function(cb) {}

/**
 * The dispose method destroys a domain, and makes a best effort attempt to
 * clean up any and all IO that is associated with the domain. Streams are
 * aborted, ended, closed, and/or destroyed. Timers are cleared.
 */
domain.Domain.prototype.dispose = function() {}

/**
 * An array of timers and event emitters that have been explicitly added to
 * the domain.
 */
domain.Domain.prototype.members = 0;

exports = domain;

