/**
 * This module has utilities for URL resolution and parsing.
 */
var url = {};

/**
 * Take a URL string, and return an object.
 * @param urlStr
 * @param parseQueryString
 * @param slashesDenoteHost
 * @returns {URL}
 */
url.parse = function(urlStr, parseQueryString, slashesDenoteHost) {}

/**
 * Take a base URL, and a href URL, and resolve them as a browser would for
 * an anchor tag.
 * @param from
 * @param to
 */
url.resolve = function(from, to) {}

/**
 * Take a parsed URL object, and return a formatted URL string.
 * @param urlObj
 */
url.format = function(urlObj) {}

/* see http://nodejs.org/docs/v0.6.12/api/url.html#url_url */
function URL() {}
URL.prototype = {
    "href": "",
    "protocol": "",
    "host": "",
    "auth": "",
    "hostname": "",
    "port": "",
    "pathname": "",
    "search": "",
    "path": "",
    "query": "",
    "hash": "",
};

exports = url;

