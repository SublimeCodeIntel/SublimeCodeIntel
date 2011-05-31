/**
 * HTTPS is the HTTP protocol over TLS/SSL. In Node this is implemented as
 * a separate module.
 */
var https = {};

/**
 * Returns a new HTTPS web server object. The options is similer to
 * tls.createServer(). The requestListener is a function which is
 * automatically added to the 'request' event.
 * @returns https.Server
 */
https.createServer = function() {}

/**
 * Like http.get() but for HTTPS.
 * @returns http.ClientRequest
 */
https.get = function() {}

/**
 * Makes a request to a secure web server. Similar options to
 * http.request().
 * @returns http.ClientRequest
 */
https.request = function() {}

/**
 * This class is a subclass of tls.Server and emits events same as
 * http.Server. See http.Server for more information.
 */
https.Server = function() {}
https.Server.prototype = {}


                var http = require('http');
                https.Server.prototype = new http.Server();
                exports = https;

