/**
 * You can access this module with:
 */
var zlib = {};

/**
 * Returns a new Gzip object with an options.
 * @param options
 * @returns {zlib.Gzip} a new Gzip object with an options
 */
zlib.createGzip = function(options) {}

/**
 * Returns a new Gunzip object with an options.
 * @param options
 * @returns {zlib.Gunzip} a new Gunzip object with an options
 */
zlib.createGunzip = function(options) {}

/**
 * Returns a new Deflate object with an options.
 * @param options
 * @returns {zlib.Deflate} a new Deflate object with an options
 */
zlib.createDeflate = function(options) {}

/**
 * Returns a new Inflate object with an options.
 * @param options
 * @returns {zlib.Inflate} a new Inflate object with an options
 */
zlib.createInflate = function(options) {}

/**
 * Returns a new DeflateRaw object with an options.
 * @param options
 * @returns {zlib.DeflateRaw} a new DeflateRaw object with an options
 */
zlib.createDeflateRaw = function(options) {}

/**
 * Returns a new InflateRaw object with an options.
 * @param options
 * @returns {zlib.InflateRaw} a new InflateRaw object with an options
 */
zlib.createInflateRaw = function(options) {}

/**
 * Returns a new Unzip object with an options.
 * @param options
 * @returns {zlib.Unzip} a new Unzip object with an options
 */
zlib.createUnzip = function(options) {}

/**
 * Compress a string with Deflate.
 * @param buf
 * @param callback
 */
zlib.deflate = function(buf, callback) {}

/**
 * Compress a string with DeflateRaw.
 * @param buf
 * @param callback
 */
zlib.deflateRaw = function(buf, callback) {}

/**
 * Compress a string with Gzip.
 * @param buf
 * @param callback
 */
zlib.gzip = function(buf, callback) {}

/**
 * Decompress a raw Buffer with Gunzip.
 * @param buf
 * @param callback
 */
zlib.gunzip = function(buf, callback) {}

/**
 * Decompress a raw Buffer with Inflate.
 * @param buf
 * @param callback
 */
zlib.inflate = function(buf, callback) {}

/**
 * Decompress a raw Buffer with InflateRaw.
 * @param buf
 * @param callback
 */
zlib.inflateRaw = function(buf, callback) {}

/**
 * Decompress a raw Buffer with Unzip.
 * @param buf
 * @param callback
 */
zlib.unzip = function(buf, callback) {}

/**
 * Compress data using gzip.
 * @constructor
 */
zlib.Gzip = function() {}
zlib.Gzip.prototype = new stream.ReadableStream();
zlib.Gzip.prototype = new stream.WritableStream();

/**
 * Decompress a gzip stream.
 * @constructor
 */
zlib.Gunzip = function() {}
zlib.Gunzip.prototype = new stream.ReadableStream();
zlib.Gunzip.prototype = new stream.WritableStream();

/**
 * Compress data using deflate.
 * @constructor
 */
zlib.Deflate = function() {}
zlib.Deflate.prototype = new stream.ReadableStream();
zlib.Deflate.prototype = new stream.WritableStream();

/**
 * Decompress a deflate stream.
 * @constructor
 */
zlib.Inflate = function() {}
zlib.Inflate.prototype = new stream.ReadableStream();
zlib.Inflate.prototype = new stream.WritableStream();

/**
 * Compress data using deflate, and do not append a zlib header.
 * @constructor
 */
zlib.DeflateRaw = function() {}
zlib.DeflateRaw.prototype = new stream.ReadableStream();
zlib.DeflateRaw.prototype = new stream.WritableStream();

/**
 * Decompress a raw deflate stream.
 * @constructor
 */
zlib.InflateRaw = function() {}
zlib.InflateRaw.prototype = new stream.ReadableStream();
zlib.InflateRaw.prototype = new stream.WritableStream();

/**
 * Decompress either a Gzip- or Deflate-compressed stream by auto-detecting
 * the header.
 * @constructor
 */
zlib.Unzip = function() {}
zlib.Unzip.prototype = new stream.ReadableStream();
zlib.Unzip.prototype = new stream.WritableStream();

/* constants */
zlib.Z_OK = 0;
zlib.Z_STREAM_END = 0;
zlib.Z_NEED_DICT = 0;
zlib.Z_ERRNO = 0;
zlib.Z_STREAM_ERROR = 0;
zlib.Z_DATA_ERROR = 0;
zlib.Z_MEM_ERROR = 0;
zlib.Z_BUF_ERROR = 0;
zlib.Z_VERSION_ERROR = 0;
zlib.Z_NO_COMPRESSION = 0;
zlib.Z_BEST_SPEED = 0;
zlib.Z_BEST_COMPRESSION = 0;
zlib.Z_DEFAULT_COMPRESSION = 0;
zlib.Z_FILTERED = 0;
zlib.Z_HUFFMAN_ONLY = 0;
zlib.Z_RLE = 0;
zlib.Z_FIXED = 0;
zlib.Z_DEFAULT_STRATEGY = 0;
zlib.Z_BINARY = 0;
zlib.Z_TEXT = 0;
zlib.Z_ASCII = 0;
zlib.Z_UNKNOWN = 0;
zlib.Z_DEFLATED = 0;
zlib.Z_NULL = 0;
var stream = require('stream');

exports = zlib;

