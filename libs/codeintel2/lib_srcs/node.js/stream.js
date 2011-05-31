/**
 * A stream is an abstract interface implemented by various objects in
 * Node. For example a request to an HTTP server is a stream, as is stdout.
 * Streams are readable, writable, or both. All streams are instances of
 * EventEmitter.
 */
var stream = {};

stream.ReadableStream = function() {}
stream.ReadableStream.prototype = {}
/**
 * Pauses the incoming 'data' events.
 */
stream.ReadableStream.prototype.pause = function() {}
/**
 * Makes the data event emit a string instead of a Buffer. encoding can be
 * 'utf8', 'ascii', or 'base64'.
 */
stream.ReadableStream.prototype.setEncoding = function() {}
/**
 * Resumes the incoming 'data' events after a pause().
 */
stream.ReadableStream.prototype.resume = function() {}
/**
 * A boolean that is true by default, but turns false after an 'error'
 * occurred, the stream came to an 'end', or destroy() was called.
 *
 * @type {Boolean}
 */
stream.ReadableStream.prototype.readable = 0;
/**
 * This is a Stream.prototype method available on all Streams.
 */
stream.ReadableStream.prototype.pipe = function() {}
/**
 * Closes the underlying file descriptor. Stream will not emit any more
 * events.
 */
stream.ReadableStream.prototype.destroy = function() {}
/**
 * After the write queue is drained, close the file descriptor.
 */
stream.ReadableStream.prototype.destroySoon = function() {}

stream.WritableStream = function() {}
stream.WritableStream.prototype = {}
/**
 * A boolean that is true by default, but turns false after an 'error'
 * occurred or end() / destroy() was called.
 *
 * @type {Boolean}
 */
stream.WritableStream.prototype.writable = 0;
/**
 * Same as the above except with a raw buffer.
 */
stream.WritableStream.prototype.write = function() {}
/**
 * Same as above but with a buffer.
 */
stream.WritableStream.prototype.end = function() {}
/**
 * After the write queue is drained, close the file descriptor.
 * destroySoon() can still destroy straight away, as long as there is no
 * data left in the queue for writes.
 */
stream.WritableStream.prototype.destroySoon = function() {}
/**
 * Closes the underlying file descriptor. Stream will not emit any more
 * events.
 */
stream.WritableStream.prototype.destroy = function() {}


                /* all streams inherit from EventEmitter */
                var events = require('events');
                stream.ReadableStream.prototype = new events.EventEmitter();
                stream.WritableStream.prototype = new events.EventEmitter();
                exports = stream;

