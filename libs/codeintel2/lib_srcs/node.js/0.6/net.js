/**
 * The net module provides you with an asynchronous network wrapper. It
 * contains methods for creating both servers and clients (called streams).
 * You can include this module with require('net');
 */
var net = {};

/**
 * This object is an abstraction of a TCP or UNIX socket. net.Socket
 * instances implement a duplex Stream interface. They can be created by
 * the user and used as a client (with connect()) or they can be created by
 * Node and passed to the user through the 'connection' event of a server.
 * @constructor
 */
net.Socket = function() {}
net.Socket.prototype = new stream.ReadableStream();
net.Socket.prototype = new stream.WritableStream();
net.Socket.prototype = new events.EventEmitter();

/**
 * Disables the Nagle algorithm. By default TCP connections use the Nagle
 * algorithm, they buffer data before sending it off. Setting true for
 * noDelay will immediately fire off data each time socket.write() is
 * called.
 * @param noDelay=true {Boolean}
 */
net.Socket.prototype.setNoDelay = function(noDelay) {}

/**
 * Pauses the reading of data. That is, 'data' events will not be emitted.
 */
net.Socket.prototype.pause = function() {}

/**
 * Half-closes the socket. i.e., it sends a FIN packet. It is possible the
 * server will still send some data.
 * @param data
 * @param encoding
 */
net.Socket.prototype.end = function(data, encoding) {}

/**
 * Sets the socket to timeout after timeout milliseconds of inactivity on
 * the socket. By default net.Socket do not have a timeout.
 * @param timeout
 * @param callback
 */
net.Socket.prototype.setTimeout = function(timeout, callback) {}

/**
 * Resumes reading after a call to pause().
 */
net.Socket.prototype.resume = function() {}

/**
 * This function has been removed in v0.3. It used to upgrade the
 * connection to SSL/TLS. See the TLS section for the new API.
 */
net.Socket.prototype.setSecure = function() {}

/**
 * Returns the bound address and port of the socket as reported by the
 * operating system. Returns an object with two properties, e.g.
 * @returns {Object}
 */
net.Socket.prototype.address = function() {}

/**
 * The string representation of the remote IP address. For example,
 * '74.125.127.100' or '2001:4860:a005::68'.
 * @type {String}
 */
net.Socket.prototype.remoteAddress = 0;

/**
 * Sends data on the socket. The second parameter specifies the encoding in
 * the case of a string--it defaults to UTF8 encoding.
 * @param data
 * @param encoding='utf-8' {String}
 * @param callback
 */
net.Socket.prototype.write = function(data, encoding, callback) {}

/**
 * Write data with the optional encoding. The callback will be made when
 * the data is flushed to the kernel.
 * @param data
 * @param encoding='utf-8' {String}
 * @param callback
 */
net.Socket.prototype.write = function(data, encoding, callback) {}

/**
 * Opens the connection for a given socket. If port and host are given,
 * then the socket will be opened as a TCP socket, if host is omitted,
 * localhost will be assumed. If a path is given, the socket will be opened
 * as a unix socket to that path.
 * @param path
 * @param connectListener
 */
net.Socket.prototype.connect = function(path, connectListener) {}

/**
 * Opens the connection for a given socket. If port and host are given,
 * then the socket will be opened as a TCP socket, if host is omitted,
 * localhost will be assumed. If a path is given, the socket will be opened
 * as a unix socket to that path.
 * @param path
 * @param connectListener
 */
net.Socket.prototype.connect = function(path, connectListener) {}

/**
 * Ensures that no more I/O activity happens on this socket. Only necessary
 * in case of errors (parse error or so).
 */
net.Socket.prototype.destroy = function() {}

/**
 * Sets the encoding (either 'ascii', 'utf8', or 'base64') for data that is
 * received. Defaults to null.
 * @param encoding=null
 */
net.Socket.prototype.setEncoding = function(encoding) {}

/**
 * Enable/disable keep-alive functionality, and optionally set the initial
 * delay before the first keepalive probe is sent on an idle socket.
 * @param enable
 * @param initialDelay
 */
net.Socket.prototype.setKeepAlive = function(enable, initialDelay) {}

/**
 * net.Socket has the property that socket.write() always works. This is to
 * help users get up and running quickly. The computer cannot always keep
 * up with the amount of data that is written to a socket - the network
 * connection simply might be too slow. Node will internally queue up the
 * data written to a socket and send it out over the wire when it is
 * possible. (Internally it is polling on the socket's file descriptor for
 * being writable).
 */
net.Socket.prototype.bufferSize = 0;

/**
 * Construct a new socket object.
 * @param options
 */
net.Socket.prototype.Socket = function(options) {}

/**
 * The amount of received bytes.
 */
net.Socket.prototype.bytesRead = 0;

/**
 * The amount of bytes sent.
 */
net.Socket.prototype.bytesWritten = 0;

/**
 * The numeric representation of the remote port. For example, 80 or 21.
 */
net.Socket.prototype.remotePort = 0;

/** @__local__ */ net.Socket.__events__ = {};

/**
 * Emitted when a socket connection is successfully established. See
 * connect().
 */
net.Socket.__events__.connect = function() {};

/**
 * Emitted when data is received. The argument data will be a Buffer or
 * String. Encoding of data is set by socket.setEncoding(). (See the
 * Readable Stream section for more information.) Note that the data will
 * be lost if there is no listener when a Socket emits a 'data' event.
 */
net.Socket.__events__.data = function() {};

/**
 * Emitted when the other end of the socket sends a FIN packet. By default
 * (allowHalfOpen == false) the socket will destroy its file descriptor
 * once it has written out its pending write queue. However, by setting
 * allowHalfOpen == true the socket will not automatically end() its side
 * allowing the user to write arbitrary amounts of data, with the caveat
 * that the user is required to end() their side now.
 */
net.Socket.__events__.end = function() {};

/**
 * Emitted if the socket times out from inactivity. This is only to notify
 * that the socket has been idle. The user must manually close the
 * connection. See also: socket.setTimeout()
 */
net.Socket.__events__.timeout = function() {};

/**
 * Emitted when the write buffer becomes empty. Can be used to throttle
 * uploads. See also: the return values of socket.write()
 */
net.Socket.__events__.drain = function() {};

/**
 * Emitted when an error occurs. The 'close' event will be called directly
 * following this event.
 */
net.Socket.__events__.error = function() {};

/**
 * Emitted once the socket is fully closed. The argument had_error is a
 * boolean which says if the socket was closed due to a transmission error.
 */
net.Socket.__events__.close = function() {};

/**
 * Tests if input is an IP address. Returns 0 for invalid strings, returns
 * 4 for IP version 4 addresses, and returns 6 for IP version 6 addresses.
 * @param input
 * @returns {Number}
 */
net.isIP = function(input) {}

/**
 * Returns true if input is a version 6 IP address, otherwise returns
 * false.
 * @param input
 * @returns {Boolean}
 */
net.isIPv6 = function(input) {}

/**
 * Returns true if input is a version 4 IP address, otherwise returns
 * false.
 * @param input
 * @returns {Boolean}
 */
net.isIPv4 = function(input) {}

/**
 * Creates a new TCP server. The connectionListener argument is
 * automatically set as a listener for the 'connection' event.
 * @param options
 * @param connectionListener
 * @returns {net.Server}
 */
net.createServer = function(options, connectionListener) {}

/**
 * This class is used to create a TCP or UNIX server.
 * @constructor
 */
net.Server = function() {}
net.Server.prototype = new events.EventEmitter();

/**
 * The number of concurrent connections on the server.
 */
net.Server.prototype.connections = 0;

/**
 * Set this property to reject connections when the server's connection
 * count gets high.
 */
net.Server.prototype.maxConnections = 0;

/**
 * Stops the server from accepting new connections. This function is
 * asynchronous, the server is finally closed when the server emits a
 * 'close' event.
 */
net.Server.prototype.close = function() {}

/**
 * Returns the bound address and port of the server as reported by the
 * operating system.
 * @returns the bound address and port of the server as reported by the operating system
 */
net.Server.prototype.address = function() {}

/**
 * Begin accepting connections on the specified port and host. If the host
 * is omitted, the server will accept connections directed to any IPv4
 * address (INADDR_ANY). A port value of zero will assign a random port.
 * @param port
 * @param host
 * @param listeningListener
 */
net.Server.prototype.listen = function(port, host, listeningListener) {}

/**
 * Start a UNIX socket server listening for connections on the given path.
 * @param path
 * @param listeningListener
 */
net.Server.prototype.listen = function(path, listeningListener) {}

/** @__local__ */ net.Server.__events__ = {};

/**
 * Emitted when the server has been bound after calling server.listen.
 */
net.Server.__events__.listening = function() {};

/**
 * Emitted when a new connection is made. socket is an instance of
 * net.Socket.
 * @param socket {net.Socket}
 */
net.Server.__events__.connection = function(socket) {};

/**
 * Emitted when the server closes.
 */
net.Server.__events__.close = function() {};

/**
 * Emitted when an error occurs. The 'close' event will be called directly
 * following this event. See example in discussion of server.listen.
 * @param error {Error}
 */
net.Server.__events__.error = function(error) {};

/**
 * Construct a new socket object and opens a socket to the given location.
 * When the socket is established the 'connect' event will be emitted.
 * @param arguments
 * @returns {net.Socket}
 */
net.createConnection = function(arguments) {}

/**
 * Construct a new socket object and opens a socket to the given location.
 * When the socket is established the 'connect' event will be emitted.
 * @param arguments
 * @returns {net.Socket}
 */
net.connect = function(arguments) {}

var stream = require('stream');
var events = require('events');

exports = net;

