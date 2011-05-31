/**
 * This module has utilities for URL resolution and parsing. Call
 * require('url') to use it.
 */
var url = {};

/**
 * Take a URL string, and return an object. Pass true as the second
 * argument to also parse the query string using the querystring module.
 * @returns URL
 */
url.parse = function() {}

/**
 * Take a base URL, and a href URL, and resolve them as a browser would for
 * an anchor tag.
 */
url.resolve = function() {}

/**
 * Take a parsed URL object, and return a formatted URL string.
 */
url.format = function() {}


                /* see http://nodejs.org/docs/v0.4.2/api/url.html#uRL */
                function URL() {}
                URL.prototype = {
                    "href": 0,
                    "protocol": 0,
                    "host": 0,
                    "auth": 0,
                    "hostname": 0,
                    "port": 0,
                    "pathname": 0,
                    "search": 0,
                    "query": 0,
                    "hash": 0,
                };
                exports = url;

