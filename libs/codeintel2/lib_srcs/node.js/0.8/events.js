/**
 * Many objects in Node emit events: a net.Server emits an event each time
 * a peer connects to it, a fs.readStream emits an event when the file is
 * opened. All objects which emit events are instances of
 * events.EventEmitter.
 */
var events = {};

/**
 * To access the EventEmitter class, require('events').EventEmitter.
 * @constructor
 */
events.EventEmitter = function() {}

/**
 * Adds a listener to the end of the listeners array for the specified
 * event.
 * @param event
 * @param listener
 */
events.EventEmitter.prototype.addListener = function(event, listener) {}

/**
 * Removes all listeners, or those of the specified event.
 * @param event
 */
events.EventEmitter.prototype.removeAllListeners = function(event) {}

/**
 * By default EventEmitters will print a warning if more than 10 listeners
 * are added for a particular event. This is a useful default which helps
 * finding memory leaks.
 * @param n
 */
events.EventEmitter.prototype.setMaxListeners = function(n) {}

/**
 * Returns an array of listeners for the specified event.
 * @param event
 * @returns {Array} an array of listeners for the specified event
 */
events.EventEmitter.prototype.listeners = function(event) {}

/**
 * Execute each of the listeners in order with the supplied arguments.
 * @param event
 * @param arg1
 * @param arg2
 */
events.EventEmitter.prototype.emit = function(event, arg1, arg2) {}

/**
 * Remove a listener from the listener array for the specified event.
 * @param event
 * @param listener
 */
events.EventEmitter.prototype.removeListener = function(event, listener) {}

/**
 * Adds a one time listener for the event. This listener is invoked only
 * the next time the event is fired, after which it is removed.
 * @param event
 * @param listener
 */
events.EventEmitter.prototype.once = function(event, listener) {}

/**
 * Adds a listener to the end of the listeners array for the specified
 * event.
 * @param event
 * @param listener
 */
events.EventEmitter.prototype.on = function(event, listener) {}

/** @__local__ */ events.EventEmitter.__events__ = {};

/**
 * This event is emitted any time someone adds a new listener.
 * @param event {String}
 * @param listener {Function}
 */
events.EventEmitter.__events__.newListener = function(event, listener) {};

exports = events;

