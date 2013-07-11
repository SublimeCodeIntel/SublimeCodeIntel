
/**
 * The process object is a global object and can be accessed from anywhere.
 * @type {Object}
 */
var process = {};
process.__proto__ = events.EventEmitter;

/**
 * Note: this function is only available on POSIX platforms (i.e. not
 * Windows)
 * @param id
 */
process.setuid = function(id) {}

/**
 * On the next loop around the event loop call this callback.
 * @param callback
 */
process.nextTick = function(callback) {}

/**
 * A Writable Stream to stdout.
 * @type {tty.WriteStream}
 */
process.stdout = 0;

/**
 * The PID of the process.
 */
process.pid = 0;

/**
 * Returns an object describing the memory usage of the Node process
 * measured in bytes.
 * @returns an object describing the memory usage of the Node process measured in bytes
 */
process.memoryUsage = function() {}

/**
 * Send a signal to a process. pid is the process id and signal is the
 * string describing the signal to send. Signal names are strings like
 * 'SIGINT' or 'SIGUSR1'. If omitted, the signal will be 'SIGTERM'.
 * @param pid
 * @param signal='SIGTERM' {String}
 */
process.kill = function(pid, signal) {}

/**
 * Note: this function is only available on POSIX platforms (i.e. not
 * Windows)
 */
process.getgid = function() {}

/**
 * Getter/setter to set what is displayed in 'ps'.
 */
process.title = 0;

/**
 * Sets or reads the process's file mode creation mask. Child processes
 * inherit the mask from the parent process. Returns the old mask if mask
 * argument is given, otherwise returns the current mask.
 * @param mask
 * @returns the old mask if mask argument is given, otherwise returns the current mask
 */
process.umask = function(mask) {}

/**
 * What platform you're running on:
 */
process.platform = 0;

/**
 * A compiled-in property that exposes NODE_VERSION.
 */
process.version = 0;

/**
 * Ends the process with the specified code. If omitted, exit uses the
 * 'success' code 0.
 * @param code=0 {Number}
 */
process.exit = function(code) {}

/**
 * An object containing the user environment. See environ(7).
 */
process.env = 0;

/**
 * Returns the current working directory of the process.
 * @returns the current working directory of the process
 */
process.cwd = function() {}

/**
 * Note: this function is only available on POSIX platforms (i.e. not
 * Windows)
 * @param id
 */
process.setgid = function(id) {}

/**
 * An array containing the command line arguments. The first element will
 * be 'node', the second element will be the name of the JavaScript file.
 * The next elements will be any additional command line arguments.
 */
process.argv = 0;

/**
 * Changes the current working directory of the process or throws an
 * exception if that fails.
 * @param directory
 */
process.chdir = function(directory) {}

/**
 * Note: this function is only available on POSIX platforms (i.e. not
 * Windows)
 */
process.getuid = function() {}

/**
 * A Readable Stream for stdin. The stdin stream is paused by default, so
 * one must call process.stdin.resume() to read from it.
 * @type {tty.ReadStream}
 */
process.stdin = 0;

/**
 * A writable stream to stderr.
 * @type {tty.WriteStream}
 */
process.stderr = 0;

/**
 * This is the absolute pathname of the executable that started the
 * process.
 */
process.execPath = 0;

/**
 * This causes node to emit an abort. This will cause node to exit and
 * generate a core file.
 */
process.abort = function() {}

/**
 * What processor architecture you're running on: 'arm', 'ia32', or 'x64'.
 * @type {String}
 */
process.arch = 0;

/**
 * An Object containing the JavaScript representation of the configure
 * options that were used to compile the current node executable. This is
 * the same as the "config.gypi" file that was produced when running the
 * ./configure script.
 */
process.config = 0;

/**
 * Returns the current high-resolution real time in a [seconds,
 * nanoseconds] tuple Array. It is relative to an arbitrary time in the
 * past. It is not related to the time of day and therefore not subject to
 * clock drift. The primary use is for measuring performance between
 * intervals.
 * @returns the current high-resolution real time in a [seconds, nanoseconds] tuple Array
 */
process.hrtime = function() {}

/**
 * Number of seconds Node has been running.
 */
process.uptime = function() {}

/**
 * A property exposing version strings of node and its dependencies.
 */
process.versions = 0;

/** @__local__ */ process.__events__ = {};

/**
 * Emitted when the process is about to exit. This is a good hook to
 * perform constant time checks of the module's state (like for unit
 * tests). The main event loop will no longer be run after the 'exit'
 * callback finishes, so timers may not be scheduled. Example of listening
 * for exit:
 */
process.__events__.exit = function() {};

/**
 * Emitted when an exception bubbles all the way back to the event loop. If
 * a listener is added for this exception, the default action (which is to
 * print a stack trace and exit) will not occur. Example of listening for
 * uncaughtException: Note that uncaughtException is a very crude mechanism
 * for exception handling. Using try / catch in your program will give you
 * more control over your program's flow. Especially for server programs
 * that are designed to stay running forever, uncaughtException can be a
 * useful safety mechanism.
 * @param err {Error}
 */
process.__events__.uncaughtException = function(err) {};

/* required for stdin/stdout/stderr */
var tty = require('tty');

exports = process;

