/**
 * To use the HTTP server and client one must require('http').
 */
var http = {};

/**
 * Since most requests are GET requests without bodies, Node provides this
 * convenience method. The only difference between this method and
 * http.request() is that it sets the method to GET and calls req.end()
 * automatically.
 * @returns http.ClientRequest
 */
http.get = function() {}

/**
 * This object is created internally by a HTTP server -- not by the user --
 * and passed as the first argument to a 'request' listener.
 */
http.ServerRequest = function() {}
http.ServerRequest.prototype = {}
/**
 * Pauses request from emitting events. Useful to throttle back an upload.
 */
http.ServerRequest.prototype.pause = function() {}
/**
 * Set the encoding for the request body. Either 'utf8' or 'binary'.
 * Defaults to null, which means that the 'data' event will emit a Buffer
 * object..
 */
http.ServerRequest.prototype.setEncoding = function() {}
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
 * The net.Stream object associated with the connection.
 */
http.ServerRequest.prototype.connection = 0;
/**
 * The request method as a string. Read only. Example: 'GET', 'DELETE'.
 */
http.ServerRequest.prototype.method = 0;
/**
 * The HTTP protocol version as a string. Read only. Examples: '1.1',
 * '1.0'. Also request.httpVersionMajor is the first integer and
 * request.httpVersionMinor is the second.
 */
http.ServerRequest.prototype.httpVersion = 0;

/**
 * This object is created when making a request with http.request(). It is
 * passed to the 'response' event of the request object.
 */
http.ClientResponse = function() {}
http.ClientResponse.prototype = {}
/**
 * Pauses response from emitting events. Useful to throttle back a
 * download.
 */
http.ClientResponse.prototype.pause = function() {}
/**
 * Set the encoding for the response body. Either 'utf8', 'ascii', or
 * 'base64'. Defaults to null, which means that the 'data' event will emit
 * a Buffer object..
 */
http.ClientResponse.prototype.setEncoding = function() {}
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
 * '1.0'. Also response.httpVersionMajor is the first integer and
 * response.httpVersionMinor is the second.
 */
http.ClientResponse.prototype.httpVersion = 0;

/**
 * Node maintains several connections per server to make HTTP requests.
 * This function allows one to transparently issue requests.
 * @returns http.ClientRequest
 */
http.request = function() {}

http.Agent = function() {}
http.Agent.prototype = {}
/**
 * A queue of requests waiting to be sent to sockets.
 */
http.Agent.prototype.queue = 0;
/**
 * An array of sockets currently in use by the Agent. Do not modify.
 */
http.Agent.prototype.sockets = 0;
/**
 * By default set to 5. Determines how many concurrent sockets the agent
 * can have open.
 */
http.Agent.prototype.maxSockets = 0;

/**
 * This is an EventEmitter with the following events:
 */
http.Server = function() {}
http.Server.prototype = {}
/**
 * Stops the server from accepting new connections.
 */
http.Server.prototype.close = function() {}
/**
 * Start a UNIX socket server listening for connections on the given path.
 */
http.Server.prototype.listen = function() {}

/**
 * Returns a new web server object.
 * @returns http.Server
 */
http.createServer = function() {}

/**
 * This object is created internally by a HTTP server--not by the user. It
 * is passed as the second parameter to the 'request' event. It is a
 * Writable Stream.
 */
http.ServerResponse = function() {}
http.ServerResponse.prototype = {}
/**
 * Removes a header that's queued for implicit sending.
 */
http.ServerResponse.prototype.removeHeader = function() {}
/**
 * This method signals to the server that all of the response headers and
 * body has been sent; that server should consider this message complete.
 * The method, response.end(), MUST be called on each response.
 */
http.ServerResponse.prototype.end = function() {}
/**
 * Reads out a header that's already been queued but not sent to the
 * client. Note that the name is case insensitive. This can only be called
 * before headers get implicitly flushed.
 */
http.ServerResponse.prototype.getHeader = function() {}
/**
 * Sends a response header to the request. The status code is a 3-digit
 * HTTP status code, like 404. The last argument, headers, are the response
 * headers. Optionally one can give a human-readable reasonPhrase as the
 * second argument.
 */
http.ServerResponse.prototype.writeHead = function() {}
/**
 * If this method is called and response.writeHead() has not been called,
 * it will switch to implicit header mode and flush the implicit headers.
 */
http.ServerResponse.prototype.write = function() {}
/**
 * Sends a HTTP/1.1 100 Continue message to the client, indicating that the
 * request body should be sent. See the checkContinue event on Server.
 */
http.ServerResponse.prototype.writeContinue = function() {}
/**
 * This method adds HTTP trailing headers (a header but at the end of the
 * message) to the response.
 */
http.ServerResponse.prototype.addTrailers = function() {}
/**
 * Sets a single header value for implicit headers. If this header already
 * exists in the to-be-sent headers, it's value will be replaced. Use an
 * array of strings here if you need to send multiple headers with the same
 * name.
 */
http.ServerResponse.prototype.setHeader = function() {}
/**
 * When using implicit headers (not calling response.writeHead()
 * explicitly), this property controls the status code that will be send to
 * the client when the headers get flushed.
 */
http.ServerResponse.prototype.statusCode = 0;

/**
 * This object is created internally and returned from http.request(). It
 * represents an in-progress request whose header has already been queued.
 * The header is still mutable using the setHeader(name, value),
 * getHeader(name), removeHeader(name) API. The actual header will be sent
 * along with the first data chunk or when closing the connection.
 */
http.ClientRequest = function() {}
http.ClientRequest.prototype = {}
/**
 * Sends a chunk of the body. By calling this method many times, the user
 * can stream a request body to a server--in that case it is suggested to
 * use the ['Transfer-Encoding', 'chunked'] header line when creating the
 * request.
 */
http.ClientRequest.prototype.write = function() {}
/**
 * Aborts a request. (New since v0.3.8.)
 */
http.ClientRequest.prototype.abort = function() {}
/**
 * Finishes sending the request. If any parts of the body are unsent, it
 * will flush them to the stream. If the request is chunked, this will send
 * the terminating '0\r\n\r\n'.
 */
http.ClientRequest.prototype.end = function() {}

/**
 * http.request() uses a special Agent for managing multiple connections to
 * an HTTP server. Normally Agent instances should not be exposed to user
 * code, however in certain situations it's useful to check the status of
 * the agent. The http.getAgent() function allows you to access the agents.
 * @returns http.Agent
 */
http.getAgent = function() {}


                var events = require('events');
                http.Server.prototype = new events.EventEmitter();
                http.ServerRequest.prototype = new events.EventEmitter();
                http.ClientRequest.prototype = new events.EventEmitter();
                http.ClientResponse.prototype = new events.EventEmitter();
                var stream = require('stream');
                http.ServerResponse.prototype = new stream.WritableStream();
                exports = http;

