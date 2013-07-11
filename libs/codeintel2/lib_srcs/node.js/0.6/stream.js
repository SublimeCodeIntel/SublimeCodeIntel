/**
 * A stream is an abstract interface implemented by various objects in
 * Node.
 */
var stream = {};

/**
 * A Readable Stream has the following methods, members, and events.
 * @constructor
 */
stream.ReadableStream = function() {}
stream.ReadableStream.prototype = new events.EventEmitter();

/**
 * Pauses the incoming 'data' events.
 */
stream.ReadableStream.prototype.pause = function() {}

/**
 * Makes the data event emit a string instead of a Buffer. encoding can be
 * 'utf8', 'ascii', or 'base64'.
 * @param encoding
 */
stream.ReadableStream.prototype.setEncoding = function(encoding) {}

/**
 * Resumes the incoming 'data' events after a pause().
 */
stream.ReadableStream.prototype.resume = function() {}

/**
 * A boolean that is true by default, but turns false after an 'error'
 * occurred, the stream came to an 'end', or destroy() was called.
 * @type {Boolean}
 */
stream.ReadableStream.prototype.readable = 0;

/**
 * This is a Stream.prototype method available on all Streams.
 * @param destination
 * @param options
 */
stream.ReadableStream.prototype.pipe = function(destination, options) {}

/**
 * Closes the underlying file descriptor. Stream will not emit any more
 * events.
 */
stream.ReadableStream.prototype.destroy = function() {}

/**
 * After the write queue is drained, close the file descriptor.
 */
stream.ReadableStream.prototype.destroySoon = function() {}

/** @__local__ */ stream.ReadableStream.__events__ = {};

/**
 * The 'data' event emits either a Buffer (by default) or a string if
 * setEncoding() was used. Note that the data will be lost if there is no
 * listener when a Readable Stream emits a 'data' event.
 * @param data {buffer.Buffer}
 */
stream.ReadableStream.__events__.data = function(data) {};

/**
 * Emitted when the stream has received an EOF (FIN in TCP terminology).
 * Indicates that no more 'data' events will happen. If the stream is also
 * writable, it may be possible to continue writing.
 */
stream.ReadableStream.__events__.end = function() {};

/**
 * Emitted if there was an error receiving data.
 * @param exception {Error}
 */
stream.ReadableStream.__events__.error = function(exception) {};

/**
 * Emitted when the underlying file descriptor has been closed. Not all
 * streams will emit this. (For example, an incoming HTTP request will not
 * emit 'close'.)
 */
stream.ReadableStream.__events__.close = function() {};

/**
 * A Writable Stream has the following methods, members, and events.
 * @constructor
 */
stream.WritableStream = function() {}
stream.WritableStream.prototype = new events.EventEmitter();

/**
 * A boolean that is true by default, but turns false after an 'error'
 * occurred or end() / destroy() was called.
 * @type {Boolean}
 */
stream.WritableStream.prototype.writable = 0;

/**
 * Writes string with the given encoding to the stream. Returns true if the
 * string has been flushed to the kernel buffer. Returns false to indicate
 * that the kernel buffer is full, and the data will be sent out in the
 * future. The 'drain' event will indicate when the kernel buffer is empty
 * again. The encoding defaults to 'utf8'.
 * @param string
 * @param encoding='utf8' {String}
 * @param fd
 * @returns true if the string has been flushed to the kernel buffer
 */
stream.WritableStream.prototype.write = function(string, encoding, fd) {}

/**
 * Same as the above except with a raw buffer.
 * @param buffer
 */
stream.WritableStream.prototype.write = function(buffer) {}

/**
 * Terminates the stream with EOF or FIN.
 */
stream.WritableStream.prototype.end = function() {}

/**
 * Sends string with the given encoding and terminates the stream with EOF
 * or FIN. This is useful to reduce the number of packets sent.
 * @param string
 * @param encoding
 */
stream.WritableStream.prototype.end = function(string, encoding) {}

/**
 * Same as above but with a buffer.
 * @param buffer
 */
stream.WritableStream.prototype.end = function(buffer) {}

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

/** @__local__ */ stream.WritableStream.__events__ = {};

/**
 * After a write() method returned false, this event is emitted to indicate
 * that it is safe to write again.
 */
stream.WritableStream.__events__.drain = function() {};

/**
 * Emitted on error with the exception exception.
 * @param exception {Error}
 */
stream.WritableStream.__events__.error = function(exception) {};

/**
 * Emitted when the underlying file descriptor has been closed.
 */
stream.WritableStream.__events__.close = function() {};

/**
 * Emitted when the stream is passed to a readable stream's pipe method.
 * @param src {stream.ReadableStream}
 */
stream.WritableStream.__events__.pipe = function(src) {};

var events = require('events');

exports = stream;

