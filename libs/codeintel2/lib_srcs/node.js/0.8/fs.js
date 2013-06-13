/**
 * File I/O is provided by simple wrappers around standard POSIX functions.
 * To use this module do require('fs'). All the methods have asynchronous
 * and synchronous forms.
 */
var fs = {};

/**
 * Asynchronous rename(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param oldPath
 * @param newPath
 * @param callback
 */
fs.rename = function(oldPath, newPath, callback) {}

/**
 * Synchronous version of buffer-based fs.write(). Returns the number of
 * bytes written.
 * @param fd
 * @param buffer
 * @param offset
 * @param length
 * @param position
 * @returns {Number} the number of bytes written
 */
fs.writeSync = function(fd, buffer, offset, length, position) {}

/**
 * Synchronous version of string-based fs.write(). encoding defaults to
 * 'utf8'. Returns the number of bytes written.
 * @param fd
 * @param str
 * @param position
 * @param encoding='utf8' {String}
 * @returns {Number} the number of bytes written
 */
fs.writeSync = function(fd, str, position, encoding) {}

/**
 * WriteStream is a Writable Stream.
 * @constructor
 */
fs.WriteStream = function() {}

/**
 * The number of bytes written so far. Does not include data that is still
 * queued for writing.
 */
fs.WriteStream.prototype.bytesWritten = 0;

/** @__local__ */ fs.WriteStream.__events__ = {};

/**
 * Emitted when the WriteStream's file is opened.
 * @param fd {Number}
 */
fs.WriteStream.__events__.open = function(fd) {};

/**
 * Synchronous chmod(2).
 * @param path
 * @param mode
 */
fs.chmodSync = function(path, mode) {}

/**
 * Objects returned from fs.stat(), fs.lstat() and fs.fstat() and their
 * synchronous counterparts are of this type.
 * @constructor
 */
fs.Stats = function() {}

/**
 * Asynchronous chmod(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param path
 * @param mode
 * @param callback
 */
fs.chmod = function(path, mode, callback) {}

/**
 * Synchronous readdir(3). Returns an array of filenames excluding '.' and
 * '..'.
 * @param path
 * @returns {Array} an array of filenames excluding '.' and '..'
 */
fs.readdirSync = function(path) {}

/**
 * Synchronous readlink(2). Returns the symbolic link's string value.
 * @param path
 * @returns {String} the symbolic link's string value
 */
fs.readlinkSync = function(path) {}

/**
 * Synchronous close(2).
 * @param fd
 */
fs.closeSync = function(fd) {}

/**
 * Asynchronous close(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param fd
 * @param callback
 */
fs.close = function(fd, callback) {}

/**
 * Asynchronous file open. See open(2). flags can be:
 * @param path
 * @param flags
 * @param mode
 * @param callback
 */
fs.open = function(path, flags, mode, callback) {}

/**
 * Synchronous lstat(2). Returns an instance of fs.Stats.
 * @param path
 * @returns {fs.Stats} an instance of fs.Stats
 */
fs.lstatSync = function(path) {}

/**
 * Synchronous link(2).
 * @param srcpath
 * @param dstpath
 */
fs.linkSync = function(srcpath, dstpath) {}

/**
 * Synchronous stat(2). Returns an instance of fs.Stats.
 * @param path
 * @returns {fs.Stats} an instance of fs.Stats
 */
fs.statSync = function(path) {}

/**
 * Asynchronous mkdir(2). No arguments other than a possible exception are
 * given to the completion callback. mode defaults to 0777.
 * @param path
 * @param mode=0777 {Number}
 * @param callback
 */
fs.mkdir = function(path, mode, callback) {}

/**
 * Asynchronously reads the entire contents of a file. Example:
 * @param filename
 * @param encoding
 * @param callback
 */
fs.readFile = function(filename, encoding, callback) {}

/**
 * Write buffer to the file specified by fd.
 * @param fd
 * @param buffer
 * @param offset
 * @param length
 * @param position
 * @param callback
 */
fs.write = function(fd, buffer, offset, length, position, callback) {}

/**
 * Synchronous realpath(2). Returns the resolved path.
 * @param path
 * @param cache
 * @returns the resolved path
 */
fs.realpathSync = function(path, cache) {}

/**
 * Asynchronously writes data to a file, replacing the file if it already
 * exists.
 * @param filename
 * @param data
 * @param encoding
 * @param callback
 */
fs.writeFile = function(filename, data, encoding, callback) {}

/**
 * Asynchronous rmdir(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param path
 * @param callback
 */
fs.rmdir = function(path, callback) {}

/**
 * Stop watching for changes on filename.
 * @param filename
 */
fs.unwatchFile = function(filename) {}

/**
 * Asynchronous fstat(2). The callback gets two arguments (err, stats)
 * where stats is a fs.Stats object. fstat() is identical to stat(), except
 * that the file to be stat-ed is specified by the file descriptor fd.
 * @param fd
 * @param callback
 */
fs.fstat = function(fd, callback) {}

/**
 * ReadStream is a Readable Stream.
 * @constructor
 */
fs.ReadStream = function() {}

/** @__local__ */ fs.ReadStream.__events__ = {};

/**
 * Emitted when the ReadStream's file is opened.
 * @param fd {Number}
 */
fs.ReadStream.__events__.open = function(fd) {};

/**
 * Asynchronous realpath(2). The callback gets two arguments (err,
 * resolvedPath). May use process.cwd to resolve relative paths. cache is
 * an object literal of mapped paths that can be used to force a specific
 * path resolution or avoid additional fs.stat calls for known real paths.
 * @param path
 * @param cache
 * @param callback
 */
fs.realpath = function(path, cache, callback) {}

/**
 * Asynchronous stat(2). The callback gets two arguments (err, stats) where
 * stats is a fs.Stats object. See the fs.Stats section below for more
 * information.
 * @param path
 * @param callback
 */
fs.stat = function(path, callback) {}

/**
 * Synchronous version of buffer-based fs.read. Returns the number of
 * bytesRead.
 * @param fd
 * @param buffer
 * @param offset
 * @param length
 * @param position
 * @returns {Number} the number of bytesRead
 */
fs.readSync = function(fd, buffer, offset, length, position) {}

/**
 * Legacy synchronous version of string-based fs.read. Returns an array
 * with the data from the file specified and number of bytes read, [string,
 * bytesRead].
 * @param fd
 * @param length
 * @param position
 * @param encoding
 * @returns an array with the data from the file specified and number of bytes read, [string, bytesRead]
 */
fs.readSync = function(fd, length, position, encoding) {}

/**
 * Asynchronous ftruncate(2). No arguments other than a possible exception
 * are given to the completion callback.
 * @param fd
 * @param len
 * @param callback
 */
fs.truncate = function(fd, len, callback) {}

/**
 * Asynchronous lstat(2). The callback gets two arguments (err, stats)
 * where stats is a fs.Stats object. lstat() is identical to stat(), except
 * that if path is a symbolic link, then the link itself is stat-ed, not
 * the file that it refers to.
 * @param path
 * @param callback
 */
fs.lstat = function(path, callback) {}

/**
 * Synchronous fstat(2). Returns an instance of fs.Stats.
 * @param fd
 * @returns {fs.Stats} an instance of fs.Stats
 */
fs.fstatSync = function(fd) {}

/**
 * The synchronous version of fs.writeFile.
 * @param filename
 * @param data
 * @param encoding
 */
fs.writeFileSync = function(filename, data, encoding) {}

/**
 * Asynchronous symlink(2). No arguments other than a possible exception
 * are given to the completion callback.
 * @param destination
 * @param path
 * @param type
 * @param callback
 */
fs.symlink = function(destination, path, type, callback) {}

/**
 * Synchronous symlink(2).
 * @param destination
 * @param path
 * @param type
 */
fs.symlinkSync = function(destination, path, type) {}

/**
 * Synchronous rmdir(2).
 * @param path
 */
fs.rmdirSync = function(path) {}

/**
 * Asynchronous link(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param srcpath
 * @param dstpath
 * @param callback
 */
fs.link = function(srcpath, dstpath, callback) {}

/**
 * Asynchronous readdir(3). Reads the contents of a directory.
 * @param path
 * @param callback
 */
fs.readdir = function(path, callback) {}

/**
 * Returns a new ReadStream object (See Readable Stream).
 * @param path
 * @param options
 * @returns {stream.ReadableStream}
 */
fs.createReadStream = function(path, options) {}

/**
 * Synchronous version of fs.readFile. Returns the contents of the
 * filename.
 * @param filename
 * @param encoding
 * @returns the contents of the filename
 */
fs.readFileSync = function(filename, encoding) {}

/**
 * Asynchronous unlink(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param path
 * @param callback
 */
fs.unlink = function(path, callback) {}

/**
 * Synchronous ftruncate(2).
 * @param fd
 * @param len
 */
fs.truncateSync = function(fd, len) {}

/**
 * Read data from the file specified by fd.
 * @param fd
 * @param buffer
 * @param offset
 * @param length
 * @param position
 * @param callback
 */
fs.read = function(fd, buffer, offset, length, position, callback) {}

/**
 * Synchronous rename(2).
 * @param oldPath
 * @param newPath
 */
fs.renameSync = function(oldPath, newPath) {}

/**
 * Synchronous mkdir(2).
 * @param path
 * @param mode
 */
fs.mkdirSync = function(path, mode) {}

/**
 * Watch for changes on filename. The callback listener will be called each
 * time the file is accessed.
 * @param filename
 * @param options
 * @param listener
 */
fs.watchFile = function(filename, options, listener) {}

/**
 * Returns a new WriteStream object (See Writable Stream).
 * @param path
 * @param options
 * @returns {stream.WritableStream}
 */
fs.createWriteStream = function(path, options) {}

/**
 * Synchronous open(2).
 * @param path
 * @param flags
 * @param mode
 */
fs.openSync = function(path, flags, mode) {}

/**
 * Asynchronous readlink(2). The callback gets two arguments (err,
 * linkString).
 * @param path
 * @param callback
 */
fs.readlink = function(path, callback) {}

/**
 * Synchronous unlink(2).
 * @param path
 */
fs.unlinkSync = function(path) {}

/**
 * Asynchronously append data to a file, creating the file if it not yet
 * exists.
 * @param filename
 * @param data
 * @param encoding
 * @param callback
 */
fs.appendFile = function(filename, data, encoding, callback) {}

/**
 * The synchronous version of fs.appendFile.
 * @param filename
 * @param data
 * @param encoding
 */
fs.appendFileSync = function(filename, data, encoding) {}

/**
 * Asynchronous chown(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param path
 * @param uid
 * @param gid
 * @param callback
 */
fs.chown = function(path, uid, gid, callback) {}

/**
 * Synchronous chown(2).
 * @param path
 * @param uid
 * @param gid
 */
fs.chownSync = function(path, uid, gid) {}

/**
 * Test whether or not the given path exists by checking with the file
 * system.
 * @param path
 * @param callback
 */
fs.exists = function(path, callback) {}

/**
 * Synchronous version of fs.exists.
 * @param path
 */
fs.existsSync = function(path) {}

/**
 * Asynchronous fchmod(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param fd
 * @param mode
 * @param callback
 */
fs.fchmod = function(fd, mode, callback) {}

/**
 * Synchronous fchmod(2).
 * @param fd
 * @param mode
 */
fs.fchmodSync = function(fd, mode) {}

/**
 * Asynchronous fchown(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param fd
 * @param uid
 * @param gid
 * @param callback
 */
fs.fchown = function(fd, uid, gid, callback) {}

/**
 * Synchronous fchown(2).
 * @param fd
 * @param uid
 * @param gid
 */
fs.fchownSync = function(fd, uid, gid) {}

/**
 * Objects returned from fs.watch() are of this type.
 * @constructor
 */
fs.FSWatcher = function() {}
fs.FSWatcher.prototype = new events.EventEmitter();

/**
 * Stop watching for changes on the given fs.FSWatcher.
 */
fs.FSWatcher.prototype.close = function() {}

/** @__local__ */ fs.FSWatcher.__events__ = {};

/**
 * Emitted when something changes in a watched directory or file. See more
 * details in fs.watch.
 * @param event {String}
 * @param filename {String}
 */
fs.FSWatcher.__events__.change = function(event, filename) {};

/**
 * Emitted when an error occurs.
 * @param exception {Error}
 */
fs.FSWatcher.__events__.error = function(exception) {};

/**
 * Asynchronous fsync(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param fd
 * @param callback
 */
fs.fsync = function(fd, callback) {}

/**
 * Synchronous fsync(2).
 * @param fd
 */
fs.fsyncSync = function(fd) {}

/**
 * Change the file timestamps of a file referenced by the supplied file
 * descriptor.
 * @param fd
 * @param atime
 * @param mtime
 */
fs.futimes = function(fd, atime, mtime) {}

/**
 * Change the file timestamps of a file referenced by the supplied file
 * descriptor.
 * @param fd
 * @param atime
 * @param mtime
 */
fs.futimesSync = function(fd, atime, mtime) {}

/**
 * Asynchronous lchmod(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param path
 * @param mode
 * @param callback
 */
fs.lchmod = function(path, mode, callback) {}

/**
 * Synchronous lchmod(2).
 * @param path
 * @param mode
 */
fs.lchmodSync = function(path, mode) {}

/**
 * Asynchronous lchown(2). No arguments other than a possible exception are
 * given to the completion callback.
 * @param path
 * @param uid
 * @param gid
 * @param callback
 */
fs.lchown = function(path, uid, gid, callback) {}

/**
 * Synchronous lchown(2).
 * @param path
 * @param uid
 * @param gid
 */
fs.lchownSync = function(path, uid, gid) {}

/**
 * Change file timestamps of the file referenced by the supplied path.
 * @param path
 * @param atime
 * @param mtime
 */
fs.utimes = function(path, atime, mtime) {}

/**
 * Change file timestamps of the file referenced by the supplied path.
 * @param path
 * @param atime
 * @param mtime
 */
fs.utimesSync = function(path, atime, mtime) {}

/**
 * Watch for changes on filename, where filename is either a file or a
 * directory. The returned object is a fs.FSWatcher.
 * @param filename
 * @param options
 * @param listener
 * @returns {fs.FSWatcher}
 */
fs.watch = function(filename, options, listener) {}

/* see http://nodejs.org/docs/v0.6.12/api/fs.html#fs.Stats */
fs.Stats.prototype = {
    isFile: function() {},
    isDirectory: function() {},
    isBlockDevice: function() {},
    isCharacterDevice: function() {},
    isSymbolicLink: function() {},
    isFIFO: function() {},
    isSocket: function() {},
};
/* required for createReadStream() / createWriteStream() */
var stream = require('stream');
var events = require('events');

exports = fs;

