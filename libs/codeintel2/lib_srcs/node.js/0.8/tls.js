/**
 * Use require('tls') to access this module.
 */
var tls = {};

/**
 * Creates a new [tls.Server][]. The connectionListener argument is
 * automatically set as a listener for the [secureConnection][] event. The
 * options object has these possibilities:
 * @param options
 * @param secureConnectionListener
 * @returns {tls.Server} a new tls.Server
 */
tls.createServer = function(options, secureConnectionListener) {}

/**
 * Creates a new client connection to the given port and host (old API) or
 * options.port and options.host. (If host is omitted, it defaults to
 * localhost.) options should be an object which specifies:
 * @param port
 * @param host
 * @param options
 * @param secureConnectListener
 * @returns {tls.CleartextStream}
 */
tls.connect = function(port, host, options, secureConnectListener) {}

/**
 * Creates a new client connection to the given port and host (old API) or
 * options.port and options.host. (If host is omitted, it defaults to
 * localhost.) options should be an object which specifies:
 * @param port
 * @param host
 * @param options
 * @param secureConnectListener
 * @returns {tls.CleartextStream}
 */
tls.connect = function(port, host, options, secureConnectListener) {}

/**
 * This class is a subclass of net.Server and has the same methods on it.
 * @constructor
 */
tls.Server = function() {}
tls.Server.prototype = new net.Server();

/**
 * The number of concurrent connections on the server.
 */
tls.Server.prototype.connections = 0;

/**
 * Stops the server from accepting new connections. This function is
 * asynchronous, the server is finally closed when the server emits a
 * 'close' event.
 */
tls.Server.prototype.close = function() {}

/**
 * Set this property to reject connections when the server's connection
 * count gets high.
 */
tls.Server.prototype.maxConnections = 0;

/**
 * Begin accepting connections on the specified port and host. If the host
 * is omitted, the server will accept connections directed to any IPv4
 * address (INADDR_ANY).
 * @param port
 * @param host
 * @param callback
 */
tls.Server.prototype.listen = function(port, host, callback) {}

/**
 * Add secure context that will be used if client request's SNI hostname is
 * matching passed hostname (wildcards can be used). credentials can
 * contain key, cert and ca.
 * @param hostname
 * @param credentials
 */
tls.Server.prototype.addContext = function(hostname, credentials) {}

/**
 * Returns the bound address, the address family name and port of the
 * server as reported by the operating system. See [net.Server.address()][]
 * for more information.
 * @returns {Object}
 */
tls.Server.prototype.address = function() {}

/** @__local__ */ tls.Server.__events__ = {};

/**
 * This event is emitted after a new connection has been successfully
 * handshaked. The argument is a instance of [CleartextStream][]. It has
 * all the common stream methods and events. cleartextStream.authorized is
 * a boolean value which indicates if the client has verified by one of the
 * supplied certificate authorities for the server. If
 * cleartextStream.authorized is false, then
 * cleartextStream.authorizationError is set to describe how authorization
 * failed. Implied but worth mentioning: depending on the settings of the
 * TLS server, you unauthorized connections may be accepted.
 * cleartextStream.npnProtocol is a string containing selected NPN
 * protocol. cleartextStream.servername is a string containing servername
 * requested with SNI.
 * @param cleartextStream
 */
tls.Server.__events__.secureConnection = function(cleartextStream) {};

/**
 * When a client connection emits an 'error' event before secure connection
 * is established - it will be forwarded here.
 * @param exception
 */
tls.Server.__events__.clientError = function(exception) {};

/**
 * Creates a new secure pair object with two streams, one of which
 * reads/writes encrypted data, and one reads/writes cleartext data.
 * @param credentials
 * @param isServer
 * @param requestCert
 * @param rejectUnauthorized
 * @returns {tls.SecurePair}
 */
tls.createSecurePair = function(credentials, isServer, requestCert, rejectUnauthorized) {}

/**
 * This is a stream on top of the Encrypted stream that makes it possible
 * to read/write an encrypted data as a cleartext data.
 * @constructor
 */
tls.CleartextStream = function() {}
tls.CleartextStream.prototype = new stream.ReadableStream();
tls.CleartextStream.prototype = new stream.WritableStream();

/**
 * Returns an object representing the peer's certificate. The returned
 * object has some properties corresponding to the field of the
 * certificate.
 * @returns {Object}
 */
tls.CleartextStream.prototype.getPeerCertificate = function() {}

/**
 * Returns an object representing the cipher name and the SSL/TLS protocol
 * version of the current connection.
 * @returns an object representing the cipher name and the SSL/TLS protocol version of the current connection
 */
tls.CleartextStream.prototype.getCipher = function() {}

/**
 * Returns the bound address, the address family name and port of the
 * underlying socket as reported by the operating system. Returns an object
 * with three properties, e.g.
 * @returns {Object}
 */
tls.CleartextStream.prototype.address = function() {}

/**
 * A boolean that is true if the peer certificate was signed by one of the
 * specified CAs, otherwise false
 * @type {Boolean}
 */
tls.CleartextStream.prototype.authorized = 0;

/**
 * The reason why the peer's certificate has not been verified. This
 * property becomes available only when cleartextStream.authorized ===
 * false.
 */
tls.CleartextStream.prototype.authorizationError = 0;

/**
 * The string representation of the remote IP address. For example,
 * '74.125.127.100' or '2001:4860:a005::68'.
 * @type {String}
 */
tls.CleartextStream.prototype.remoteAddress = 0;

/**
 * The numeric representation of the remote port. For example, 443.
 */
tls.CleartextStream.prototype.remotePort = 0;

/** @__local__ */ tls.CleartextStream.__events__ = {};

/**
 * This event is emitted after a new connection has been successfully
 * handshaked.  The listener will be called no matter if the server's
 * certificate was authorized or not. It is up to the user to test
 * cleartextStream.authorized to see if the server certificate was signed
 * by one of the specified CAs. If cleartextStream.authorized === false
 * then the error can be found in cleartextStream.authorizationError. Also
 * if NPN was used - you can check cleartextStream.npnProtocol for
 * negotiated protocol.
 */
tls.CleartextStream.__events__.secureConnect = function() {};

/**
 * Returned by tls.createSecurePair.
 * @constructor
 */
tls.SecurePair = function() {}
tls.SecurePair.prototype = new events.EventEmitter();

/** @__local__ */ tls.SecurePair.__events__ = {};

/**
 * The event is emitted from the SecurePair once the pair has successfully
 * established a secure connection. Similarly to the checking for the
 * server 'secureConnection' event, pair.cleartext.authorized should be
 * checked to confirm whether the certificate used properly authorized.
 */
tls.SecurePair.__events__.secure = function() {};

var events = require('events');
var net = require('net');
var stream = require('stream');

exports = tls;

