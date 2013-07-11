/**
 * Pure Javascript is Unicode friendly but not nice to binary data. When
 * dealing with TCP streams or the file system, it's necessary to handle
 * octet streams. Node has several strategies for manipulating, creating,
 * and consuming octet streams.
 */
var buffer = {};

/**
 * The Buffer class is a global type for dealing with binary data directly.
 * @constructor
 */
buffer.Buffer = function() {}

/**
 * Gives the actual byte length of a string. encoding defaults to 'utf8'.
 * @param string {String}
 * @param encoding='utf8' {String}
 * @returns Number
 */
buffer.Buffer.byteLength = function(string, encoding) {}

/**
 * Returns a new buffer which references the same memory as the old, but
 * offset and cropped by the start (defaults to 0) and end (defaults to
 * buffer.length) indexes.
 * @param start=0 {Number}
 * @param end=buffer.length {Number}
 * @returns {buffer.Buffer} a new buffer which references the same memory as the old, but offset and cropped by the start (defaults to 0) and end (defaults to buffer.length) indexes
 */
buffer.Buffer.prototype.slice = function(start, end) {}

/**
 * Writes string to the buffer at offset using the given encoding.
 * @param string
 * @param offset=0 {Number}
 * @param length=buffer.length - offset {Number}
 * @param encoding='utf8' {String}
 */
buffer.Buffer.prototype.write = function(string, offset, length, encoding) {}

/**
 * The size of the buffer in bytes. Note that this is not necessarily the
 * size of the contents. length refers to the amount of memory allocated
 * for the buffer object. It does not change when the contents of the
 * buffer are changed.
 */
buffer.Buffer.prototype.length = 0;

/**
 * Decodes and returns a string from buffer data encoded with encoding
 * (defaults to 'utf8') beginning at start (defaults to 0) and ending at
 * end (defaults to buffer.length).
 * @param encoding='utf8' {String}
 * @param start=0 {Number}
 * @param end=buffer.length {Number}
 */
buffer.Buffer.prototype.toString = function(encoding, start, end) {}

/**
 * Does copy between buffers. The source and target regions can be
 * overlapped.
 * @param targetBuffer
 * @param targetStart=0 {Number}
 * @param sourceStart=0 {Number}
 * @param sourceEnd=buffer.length {Number}
 */
buffer.Buffer.prototype.copy = function(targetBuffer, targetStart, sourceStart, sourceEnd) {}

/**
 * Tests if obj is a Buffer.
 * @param obj
 * @returns Boolean
 */
buffer.Buffer.isBuffer = function(obj) {}

/**
 * Fills the buffer with the specified value. If the offset (defaults to 0)
 * and end (defaults to buffer.length) are not given it will fill the
 * entire buffer.
 * @param value
 * @param offset=0 {Number}
 * @param end=buffer.length {Number}
 */
buffer.Buffer.prototype.fill = function(value, offset, end) {}

/**
 * Reads a 64 bit double from the buffer at the specified offset with
 * specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readDoubleBE = function(offset, noAssert) {}

/**
 * Reads a 64 bit double from the buffer at the specified offset with
 * specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readDoubleLE = function(offset, noAssert) {}

/**
 * Reads a 32 bit float from the buffer at the specified offset with
 * specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readFloatBE = function(offset, noAssert) {}

/**
 * Reads a 32 bit float from the buffer at the specified offset with
 * specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readFloatLE = function(offset, noAssert) {}

/**
 * Reads a signed 16 bit integer from the buffer at the specified offset
 * with specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readInt16BE = function(offset, noAssert) {}

/**
 * Reads a signed 16 bit integer from the buffer at the specified offset
 * with specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readInt16LE = function(offset, noAssert) {}

/**
 * Reads a signed 32 bit integer from the buffer at the specified offset
 * with specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readInt32BE = function(offset, noAssert) {}

/**
 * Reads a signed 32 bit integer from the buffer at the specified offset
 * with specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readInt32LE = function(offset, noAssert) {}

/**
 * Reads a signed 8 bit integer from the buffer at the specified offset.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readInt8 = function(offset, noAssert) {}

/**
 * Reads an unsigned 16 bit integer from the buffer at the specified offset
 * with specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readUInt16BE = function(offset, noAssert) {}

/**
 * Reads an unsigned 16 bit integer from the buffer at the specified offset
 * with specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readUInt16LE = function(offset, noAssert) {}

/**
 * Reads an unsigned 32 bit integer from the buffer at the specified offset
 * with specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readUInt32BE = function(offset, noAssert) {}

/**
 * Reads an unsigned 32 bit integer from the buffer at the specified offset
 * with specified endian format.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readUInt32LE = function(offset, noAssert) {}

/**
 * Reads an unsigned 8 bit integer from the buffer at the specified offset.
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 * @returns Number
 */
buffer.Buffer.prototype.readUInt8 = function(offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid 64 bit double.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeDoubleBE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid 64 bit double.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeDoubleLE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid 32 bit float.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeFloatBE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid 32 bit float.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeFloatLE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid signed 16 bit integer.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeInt16BE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid signed 16 bit integer.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeInt16LE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid signed 32 bit integer.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeInt32BE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid signed 32 bit integer.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeInt32LE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset. Note, value must be
 * a valid signed 8 bit integer.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeInt8 = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid unsigned 16 bit integer.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeUInt16BE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid unsigned 16 bit integer.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeUInt16LE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid unsigned 32 bit integer.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeUInt32BE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset with specified endian
 * format. Note, value must be a valid unsigned 32 bit integer.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeUInt32LE = function(value, offset, noAssert) {}

/**
 * Writes value to the buffer at the specified offset. Note, value must be
 * a valid unsigned 8 bit integer.
 * @param value {Number}
 * @param offset {Number}
 * @param noAssert=false {Boolean}
 */
buffer.Buffer.prototype.writeUInt8 = function(value, offset, noAssert) {}

/**
 * This class is primarily for internal use. JavaScript programs should use
 * Buffer instead of using SlowBuffer.
 * @constructor
 */
buffer.SlowBuffer = function() {}

/**
 * How many bytes will be returned when buffer.inspect() is called. This
 * can be overridden by user modules.
 */
buffer.INSPECT_MAX_BYTES = 50;

exports = buffer;

