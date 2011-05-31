/**
 * File I/O is provided by simple wrappers around standard POSIX functions.
 * To use this module do require('fs'). All the methods have asynchronous
 * and synchronous forms.
 */
var fs = {};

/**
 * Asynchronous rename(2). No arguments other than a possible exception are
 * given to the completion callback.
 */
fs.rename = function() {}

/**
 * Synchronous version of string-based fs.write(). Returns the number of
 * bytes written.
 */
fs.writeSync = function() {}

/**
 * WriteStream is a Writable Stream.
 */
fs.WriteStream = function() {}
fs.WriteStream.prototype = {}

/**
 * Synchronous chmod(2).
 */
fs.chmodSync = function() {}

/**
 * Objects returned from fs.stat() and fs.lstat() are of this type.
 */
fs.Stats = function() {}
fs.Stats.prototype = {}

/**
 * Asynchronous chmod(2). No arguments other than a possible exception are
 * given to the completion callback.
 */
fs.chmod = function() {}

/**
 * Synchronous readdir(3). Returns an array of filenames excluding '.' and
 * '..'.
 */
fs.readdirSync = function() {}

/**
 * Synchronous readlink(2). Returns the resolved path.
 */
fs.readlinkSync = function() {}

/**
 * Synchronous close(2).
 */
fs.closeSync = function() {}

/**
 * Asynchronous close(2). No arguments other than a possible exception are
 * given to the completion callback.
 */
fs.close = function() {}

/**
 * Asynchronous file open. See open(2). Flags can be 'r', 'r+', 'w', 'w+',
 * 'a', or 'a+'. mode defaults to 0666. The callback gets two arguments
 * (err, fd).
 */
fs.open = function() {}

/**
 * Synchronous lstat(2). Returns an instance of fs.Stats.
 * @returns Stats
 */
fs.lstatSync = function() {}

/**
 * Synchronous link(2).
 */
fs.linkSync = function() {}

/**
 * Synchronous stat(2). Returns an instance of fs.Stats.
 * @returns Stats
 */
fs.statSync = function() {}

/**
 * Asynchronous mkdir(2). No arguments other than a possible exception are
 * given to the completion callback.
 */
fs.mkdir = function() {}

/**
 * Asynchronously reads the entire contents of a file. Example:
 */
fs.readFile = function() {}

/**
 * Write buffer to the file specified by fd.
 */
fs.write = function() {}

/**
 * Synchronous realpath(2). Returns the resolved path.
 */
fs.realpathSync = function() {}

/**
 * Asynchronously writes data to a file, replacing the file if it already
 * exists. data can be a string or a buffer.
 */
fs.writeFile = function() {}

/**
 * Asynchronous rmdir(2). No arguments other than a possible exception are
 * given to the completion callback.
 */
fs.rmdir = function() {}

/**
 * Stop watching for changes on filename.
 */
fs.unwatchFile = function() {}

/**
 * Asynchronous fstat(2). The callback gets two arguments (err, stats)
 * where stats is a fs.Stats object.
 */
fs.fstat = function() {}

/**
 * ReadStream is a Readable Stream.
 */
fs.ReadStream = function() {}
fs.ReadStream.prototype = {}

/**
 * Asynchronous realpath(2). The callback gets two arguments (err,
 * resolvedPath).
 */
fs.realpath = function() {}

/**
 * Asynchronous stat(2). The callback gets two arguments (err, stats) where
 * stats is a `fs.Stats` object. It looks like this:
 */
fs.stat = function() {}

/**
 * Synchronous version of string-based fs.read. Returns the number of
 * bytesRead.
 */
fs.readSync = function() {}

/**
 * Asynchronous ftruncate(2). No arguments other than a possible exception
 * are given to the completion callback.
 */
fs.truncate = function() {}

/**
 * Asynchronous lstat(2). The callback gets two arguments (err, stats)
 * where stats is a fs.Stats object. lstat() is identical to stat(), except
 * that if path is a symbolic link, then the link itself is stat-ed, not
 * the file that it refers to.
 */
fs.lstat = function() {}

/**
 * Synchronous fstat(2). Returns an instance of fs.Stats.
 * @returns Stats
 */
fs.fstatSync = function() {}

/**
 * The synchronous version of fs.writeFile.
 */
fs.writeFileSync = function() {}

/**
 * Asynchronous symlink(2). No arguments other than a possible exception
 * are given to the completion callback.
 */
fs.symlink = function() {}

/**
 * Synchronous symlink(2).
 */
fs.symlinkSync = function() {}

/**
 * Synchronous rmdir(2).
 */
fs.rmdirSync = function() {}

/**
 * Asynchronous link(2). No arguments other than a possible exception are
 * given to the completion callback.
 */
fs.link = function() {}

/**
 * Asynchronous readdir(3). Reads the contents of a directory. The callback
 * gets two arguments (err, files) where files is an array of the names of
 * the files in the directory excluding '.' and '..'.
 */
fs.readdir = function() {}

/**
 * Returns a new ReadStream object (See Readable Stream).
 * @returns stream.ReadableStream
 */
fs.createReadStream = function() {}

/**
 * Synchronous version of fs.readFile. Returns the contents of the
 * filename.
 */
fs.readFileSync = function() {}

/**
 * Asynchronous unlink(2). No arguments other than a possible exception are
 * given to the completion callback.
 */
fs.unlink = function() {}

/**
 * Synchronous ftruncate(2).
 */
fs.truncateSync = function() {}

/**
 * Read data from the file specified by fd.
 */
fs.read = function() {}

/**
 * Synchronous rename(2).
 */
fs.renameSync = function() {}

/**
 * Synchronous mkdir(2).
 */
fs.mkdirSync = function() {}

/**
 * Watch for changes on filename. The callback listener will be called each
 * time the file is accessed.
 */
fs.watchFile = function() {}

/**
 * Returns a new WriteStream object (See Writable Stream).
 * @returns stream.WritableStream
 */
fs.createWriteStream = function() {}

/**
 * Synchronous open(2).
 */
fs.openSync = function() {}

/**
 * Asynchronous readlink(2). The callback gets two arguments (err,
 * resolvedPath).
 */
fs.readlink = function() {}

/**
 * Synchronous unlink(2).
 */
fs.unlinkSync = function() {}


                /* see http://nodejs.org/docs/v0.4.2/api/fs.html#fs.Stats */
                fs.Stats.prototype = {
                    isFile: function() {},
                    isDirectory: function() {},
                    isBlockDevice: function() {},
                    isCharacterDevice: function() {},
                    isSymbolicLink: function() {},
                    isFIFO: function() {},
                    isSocket: function() {}
                };
                /* required for createReadStream() / createWriteStream() */
                var stream = require('stream');
                exports = fs;

