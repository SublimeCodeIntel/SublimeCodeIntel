/**
 * Node provides a tri-directional popen(3) facility through the
 * child_process module.
 */
var child_process = {};

/**
 * Launches a new process with the given command, with command line
 * arguments in args.
 * @param command {String}
 * @param args {Array}
 * @param options {Object}
 * @returns {child_process.ChildProcess}
 */
child_process.spawn = function(command, args, options) {}

/**
 * ChildProcess is an EventEmitter.
 * @constructor
 */
child_process.ChildProcess = function() {}
child_process.ChildProcess.prototype = new events.EventEmitter();

/**
 * Send a signal to the child process. If no argument is given, the process
 * will be sent 'SIGTERM'. See signal(7) for a list of available signals.
 * @param signal='SIGTERM' {String}
 */
child_process.ChildProcess.prototype.kill = function(signal) {}

/**
 * A Writable Stream that represents the child process's stdin.
 * @type {stream.WritableStream}
 */
child_process.ChildProcess.prototype.stdin = 0;

/**
 * The PID of the child process.
 */
child_process.ChildProcess.prototype.pid = 0;

/**
 * A Readable Stream that represents the child process's stderr.
 * @type {stream.ReadableStream}
 */
child_process.ChildProcess.prototype.stderr = 0;

/**
 * A Readable Stream that represents the child process's stdout.
 * @type {stream.ReadableStream}
 */
child_process.ChildProcess.prototype.stdout = 0;

/**
 * Send a message (and, optionally, a handle object) to a child process.
 * @param message {Object}
 * @param sendHandle {Handle}
 */
child_process.ChildProcess.prototype.send = function(message, sendHandle) {}

/** @__local__ */ child_process.ChildProcess.__events__ = {};

/**
 * This event is emitted after the child process ends. If the process
 * terminated normally, code is the final exit code of the process,
 * otherwise null. If the process terminated due to receipt of a signal,
 * signal is the string name of the signal, otherwise null. See waitpid(2).
 * @param code=null {Number}
 * @param signal=null {String}
 */
child_process.ChildProcess.__events__.exit = function(code, signal) {};

/**
 * Runs a command in a shell and buffers the output.
 * @param command {String}
 * @param options {Object}
 * @param callback {Function}
 * @returns {child_process.ChildProcess} ChildProcess object
 */
child_process.exec = function(command, options, callback) {}

/**
 * This is similar to child_process.exec() except it does not execute a
 * subshell but rather the specified file directly. This makes it slightly
 * leaner than child_process.exec. It has the same options.
 * @param file {String}
 * @param args {Array}
 * @param options {Object}
 * @param callback {Function}
 * @returns {child_process.ChildProcess} ChildProcess object
 */
child_process.execFile = function(file, args, options, callback) {}

/**
 * This is a special case of the spawn() functionality for spawning Node
 * processes. In addition to having all the methods in a normal
 * ChildProcess instance, the returned object has a communication channel
 * built-in. The channel is written to with child.send(message,
 * [sendHandle]) and messages are received by a 'message' event on the
 * child.
 * @param modulePath {String}
 * @param args {Array}
 * @param options {Object}
 * @param callback {Function}
 * @returns {child_process.ChildProcess} ChildProcess object
 */
child_process.fork = function(modulePath, args, options, callback) {}

/* used for giving types to ChildProcess.std* */
var stream = require('stream');
var events = require('events');

exports = child_process;

