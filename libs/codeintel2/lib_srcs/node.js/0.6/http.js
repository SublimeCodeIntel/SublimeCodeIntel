/**
 * To use the HTTP server and client one must require('http').
 */
var http = {};

/**
 * Since most requests are GET requests without bodies, Node provides this
 * convenience method. The only difference between this method and
 * http.request() is that it sets the method to GET and calls req.end()
 * automatically.
 * @param options
 * @param callback
 * @returns {http.ClientRequest}
 */
http.get = function(options, callback) {}

/**
 * This object is created internally by a HTTP server -- not by the user --
 * and passed as the first argument to a 'request' listener.
 * @constructor
 */
http.ServerRequest = function() {}
http.ServerRequest.prototype = new events.EventEmitter();

/**
 * Pauses request from emitting events. Useful to throttle back an upload.
 */
http.ServerRequest.prototype.pause = function() {}

/**
 * Set the encoding for the request body. Either 'utf8' or 'binary'.
 * Defaults to null, which means that the 'data' event will emit a Buffer
 * object..
 * @param encoding=null
 */
http.ServerRequest.prototype.setEncoding = function(encoding) {}

/**
 * Resumes a paused request.
 */
http.ServerRequest.prototype.resume = function() {}

/**
 * Request URL string. This contains only the URL that is present in the
 * actual HTTP request. If the request is:
 */
http.ServerRequest.prototype.url = 0;

/**
 * Read only; HTTP trailers (if present). Only populated after the 'end'
 * event.
 */
http.ServerRequest.prototype.trailers = 0;

/**
 * Read only.
 */
http.ServerRequest.prototype.headers = 0;

/**
 * The net.Socket object associated with the connection.
 * @type {net.Socket}
 */
http.ServerRequest.prototype.connection = 0;

/**
 * The request method as a string. Read only. Example:
 * @type {String}
 */
http.ServerRequest.prototype.method = 0;

/**
 * The HTTP protocol version as a string. Read only. Examples:
 * @type {String}
 */
http.ServerRequest.prototype.httpVersion = 0;

/** @__local__ */ http.ServerRequest.__events__ = {};

/**
 * Emitted when a piece of the message body is received. The chunk is a
 * string if an encoding has been set with request.setEncoding(), otherwise
 * it's a Buffer. Note that the data will be lost if there is no listener
 * when a ServerRequest emits a 'data' event.
 * @param chunk {buffer.Buffer}
 */
http.ServerRequest.__events__.data = function(chunk) {};

/**
 * Emitted exactly once for each request. After that, no more 'data' events
 * will be emitted on the request.
 */
http.ServerRequest.__events__.end = function() {};

/**
 * Indicates that the underlaying connection was terminated before
 * response.end() was called or able to flush. Just like 'end', this event
 * occurs only once per request, and no more 'data' events will fire
 * afterwards. Note: 'close' can fire after 'end', but not vice versa.
 */
http.ServerRequest.__events__.close = function() {};

/**
 * This object is created when making a request with http.request(). It is
 * passed to the 'response' event of the request object.
 * @constructor
 */
http.ClientResponse = function() {}
http.ClientResponse.prototype = new stream.ReadableStream();

/**
 * Pauses response from emitting events. Useful to throttle back a
 * download.
 */
http.ClientResponse.prototype.pause = function() {}

/**
 * Set the encoding for the response body. Either 'utf8', 'ascii', or
 * 'base64'. Defaults to null, which means that the 'data' event will emit
 * a Buffer object.
 * @param encoding=null
 */
http.ClientResponse.prototype.setEncoding = function(encoding) {}

/**
 * Resumes a paused response.
 */
http.ClientResponse.prototype.resume = function() {}

/**
 * The response trailers object. Only populated after the 'end' event.
 */
http.ClientResponse.prototype.trailers = 0;

/**
 * The response headers object.
 */
http.ClientResponse.prototype.headers = 0;

/**
 * The 3-digit HTTP response status code. E.G. 404.
 */
http.ClientResponse.prototype.statusCode = 0;

/**
 * The HTTP version of the connected-to server. Probably either '1.1' or
 * '1.0'.
 */
http.ClientResponse.prototype.httpVersion = 0;

/** @__local__ */ http.ClientResponse.__events__ = {};

/**
 * Emitted when a piece of the message body is received. Note that the data
 * will be lost if there is no listener when a ClientResponse emits a
 * 'data' event.
 * @param chunk {buffer.Buffer}
 */
http.ClientResponse.__events__.data = function(chunk) {};

/**
 * Emitted exactly once for each message. No arguments. After emitted no
 * other events will be emitted on the response.
 */
http.ClientResponse.__events__.end = function() {};

/**
 * Indicates that the underlaying connection was terminated before end
 * event was emitted. See http.ServerRequest's 'close' event for more
 * information.
 * @param err {Error}
 */
http.ClientResponse.__events__.close = function(err) {};

/**
 * Node maintains several connections per server to make HTTP requests.
 * @param options
 * @param callback
 * @returns {http.ClientRequest}
 */
http.request = function(options, callback) {}

/**
 * In node 0.5.3+ there is a new implementation of the HTTP Agent which is
 * used for pooling sockets used in HTTP client requests.
 * @constructor
 */
http.Agent = function() {}

/**
 * An object which contains arrays of sockets currently in use by the
 * Agent. Do not  modify.
 */
http.Agent.prototype.sockets = 0;

/**
 * By default set to 5. Determines how many concurrent sockets the agent
 * can have  open per host.
 */
http.Agent.prototype.maxSockets = 0;

/**
 * An object which contains queues of requests that have not yet been
 * assigned to  sockets. Do not modify.
 */
http.Agent.prototype.requests = 0;

/**
 * This is an EventEmitter with the following events:
 * @constructor
 */
http.Server = function() {}
http.Server.prototype = new events.EventEmitter();

/**
 * Stops the server from accepting new connections.
 */
http.Server.prototype.close = function() {}

/**
 * Begin accepting connections on the specified port and hostname. If the
 * hostname is omitted, the server will accept connections directed to any
 * IPv4 address (INADDR_ANY).
 * @param port
 * @param hostname
 * @param callback
 */
http.Server.prototype.listen = function(port, hostname, callback) {}

/**
 * Start a UNIX socket server listening for connections on the given path.
 * @param path
 * @param callback
 */
http.Server.prototype.listen = function(path, callback) {}

/** @__local__ */ http.Server.__events__ = {};

/**
 * Emitted each time there is a request. Note that there may be multiple
 * requests per connection (in the case of keep-alive connections).
 * request is an instance of http.ServerRequest and response is  an
 * instance of http.ServerResponse
 * @param request {http.ServerRequest}
 * @param response {http.ServerResponse}
 */
http.Server.__events__.request = function(request, response) {};

/**
 *  When a new TCP stream is established. socket is an object of type
 * net.Socket. Usually users will not want to access this event. The
 * socket can also be accessed at request.connection.
 * @param socket {net.Socket}
 */
http.Server.__events__.connection = function(socket) {};

/**
 *  Emitted when the server closes.
 */
http.Server.__events__.close = function() {};

/**
 * Emitted each time a request with an http Expect: 100-continue is
 * received. If this event isn't listened for, the server will
 * automatically respond with a 100 Continue as appropriate. Handling this
 * event involves calling response.writeContinue if the client should
 * continue to send the request body, or generating an appropriate HTTP
 * response (e.g., 400 Bad Request) if the client should not continue to
 * send the request body. Note that when this event is emitted and handled,
 * the request event will not be emitted.
 * @param request {http.ServerRequest}
 * @param response {http.ServerResponse}
 */
http.Server.__events__.checkContinue = function(request, response) {};

/**
 * Emitted each time a client requests a http upgrade. If this event isn't
 * listened for, then clients requesting an upgrade will have their
 * connections closed. request is the arguments for the http request, as it
 * is in the request event. socket is the network socket between the server
 * and client. head is an instance of Buffer, the first packet of the
 * upgraded stream, this may be empty. After this event is emitted, the
 * request's socket will not have a data event listener, meaning you will
 * need to bind to it in order to handle data sent to the server on that
 * socket.
 * @param request {http.ServerRequest}
 * @param socket {net.Socket}
 * @param head {buffer.Buffer}
 */
http.Server.__events__.upgrade = function(request, socket, head) {};

/**
 * If a client connection emits an 'error' event - it will forwarded here.
 * @param exception {Error}
 */
http.Server.__events__.clientError = function(exception) {};

/**
 * Returns a new web server object.
 * @param requestListener {http.Server.__events__.request}
 * @returns {http.Server}
 */
http.createServer = function(requestListener) {}

/**
 * This object is created internally by a HTTP server--not by the user. It
 * is passed as the second parameter to the 'request' event.
 * @constructor
 */
http.ServerResponse = function() {}
http.ServerResponse.prototype = new stream.WritableStream();

/**
 * Removes a header that's queued for implicit sending.
 * @param name
 */
http.ServerResponse.prototype.removeHeader = function(name) {}

/**
 * This method signals to the server that all of the response headers and
 * body has been sent; that server should consider this message complete.
 * @param data
 * @param encoding
 */
http.ServerResponse.prototype.end = function(data, encoding) {}

/**
 * Reads out a header that's already been queued but not sent to the
 * client. Note that the name is case insensitive. This can only be called
 * before headers get implicitly flushed.
 * @param name
 */
http.ServerResponse.prototype.getHeader = function(name) {}

/**
 * Sends a response header to the request. The status code is a 3-digit
 * HTTP status code, like 404. The last argument, headers, are the response
 * headers.
 * @param statusCode
 * @param reasonPhrase
 * @param headers
 */
http.ServerResponse.prototype.writeHead = function(statusCode, reasonPhrase, headers) {}

/**
 * If this method is called and response.writeHead() has not been called,
 * it will switch to implicit header mode and flush the implicit headers.
 * @param chunk
 * @param encoding
 */
http.ServerResponse.prototype.write = function(chunk, encoding) {}

/**
 * Sends a HTTP/1.1 100 Continue message to the client, indicating that the
 * request body should be sent. See the checkContinue event on Server.
 */
http.ServerResponse.prototype.writeContinue = function() {}

/**
 * This method adds HTTP trailing headers (a header but at the end of the
 * message) to the response.
 * @param headers
 */
http.ServerResponse.prototype.addTrailers = function(headers) {}

/**
 * Sets a single header value for implicit headers. If this header already
 * exists in the to-be-sent headers, its value will be replaced. Use an
 * array of strings here if you need to send multiple headers with the same
 * name.
 * @param name
 * @param value
 */
http.ServerResponse.prototype.setHeader = function(name, value) {}

/**
 * When using implicit headers (not calling response.writeHead()
 * explicitly), this property controls the status code that will be send to
 * the client when the headers get flushed.
 */
http.ServerResponse.prototype.statusCode = 0;

/** @__local__ */ http.ServerResponse.__events__ = {};

/**
 * Indicates that the underlaying connection was terminated before
 * response.end() was called or able to flush.
 */
http.ServerResponse.__events__.close = function() {};

/**
 * This object is created internally and returned from http.request(). It
 * represents an in-progress request whose header has already been queued.
 * The header is still mutable using the setHeader(name, value),
 * getHeader(name), removeHeader(name) API. The actual header will be sent
 * along with the first data chunk or when closing the connection.
 * @constructor
 */
http.ClientRequest = function() {}
http.ClientRequest.prototype = new stream.WritableStream();

/**
 * Sends a chunk of the body. By calling this method many times, the user
 * can stream a request body to a server--in that case it is suggested to
 * use the ['Transfer-Encoding', 'chunked'] header line when creating the
 * request.
 * @param chunk
 * @param encoding
 */
http.ClientRequest.prototype.write = function(chunk, encoding) {}

/**
 * Aborts a request. (New since v0.3.8.)
 */
http.ClientRequest.prototype.abort = function() {}

/**
 * Finishes sending the request. If any parts of the body are unsent, it
 * will flush them to the stream. If the request is chunked, this will send
 * the terminating '0\r\n\r\n'.
 * @param data
 * @param encoding
 */
http.ClientRequest.prototype.end = function(data, encoding) {}

/**
 * Once a socket is assigned to this request and is connected
 * socket.setNoDelay(noDelay) will be called.
 * @param noDelay
 */
http.ClientRequest.prototype.setNoDelay = function(noDelay) {}

/**
 * Once a socket is assigned to this request and is connected
 * socket.setKeepAlive(enable, [initialDelay]) will be called.
 * @param enable
 * @param initialDelay
 */
http.ClientRequest.prototype.setSocketKeepAlive = function(enable, initialDelay) {}

/**
 * Once a socket is assigned to this request and is connected
 * socket.setTimeout(timeout, [callback]) will be called.
 * @param timeout
 * @param callback
 */
http.ClientRequest.prototype.setTimeout = function(timeout, callback) {}

/** @__local__ */ http.ClientRequest.__events__ = {};

/**
 * Emitted when a response is received to this request. This event is
 * emitted only once. The response argument will be an instance of
 * http.ClientResponse. Options: host: A domain name or IP address of the
 * server to issue the request to. port: Port of remote server. socketPath:
 * Unix Domain Socket (use one of host:port or socketPath)
 * @param response {http.ClientResponse}
 */
http.ClientRequest.__events__.response = function(response) {};

/**
 * Emitted after a socket is assigned to this request.
 * @param socket {net.Socket}
 */
http.ClientRequest.__events__.socket = function(socket) {};

/**
 * Emitted each time a server responds to a request with an upgrade. If
 * this event isn't being listened for, clients receiving an upgrade header
 * will have their connections closed. A client server pair that show you
 * how to listen for the upgrade event using http.getAgent:
 * @param response {http.ClientResponse}
 * @param socket {net.Socket}
 * @param head {buffer.Buffer}
 */
http.ClientRequest.__events__.upgrade = function(response, socket, head) {};

/**
 * Emitted when the server sends a '100 Continue' HTTP response, usually
 * because the request contained 'Expect: 100-continue'. This is an
 * instruction that the client should send the request body.
 */
http.ClientRequest.__events__.continue = function() {};

/**
 * Global instance of Agent which is used as the default for all http
 * client requests.
 * @type {http.Agent}
 */
http.globalAgent = 0;

var events = require('events');
var stream = require('stream');
var buffer = require('buffer');

exports = http;

