/**
 * Use require('dns') to access this module. All methods in the dns module
 * use C-Ares except for dns.lookup which uses getaddrinfo(3) in a thread
 * pool. C-Ares is much faster than getaddrinfo but the system resolver is
 * more constant with how other programs operate. When a user does
 * net.connect(80, 'google.com') or http.get({ host: 'google.com' }) the
 * dns.lookup method is used. Users who need to do a large number of look
 * ups quickly should use the methods that go through C-Ares.
 */
var dns = {};

/**
 * Resolves a domain (e.g. 'google.com') into an array of the record types
 * specified by rrtype. Valid rrtypes are 'A' (IPV4 addresses, default),
 * 'AAAA' (IPV6 addresses), 'MX' (mail exchange records), 'TXT' (text
 * records), 'SRV' (SRV records), 'PTR' (used for reverse IP lookups), 'NS'
 * (name server records) and 'CNAME' (canonical name records).
 * @param domain
 * @param rrtype
 * @param callback
 */
dns.resolve = function(domain, rrtype, callback) {}

/**
 * Reverse resolves an ip address to an array of domain names.
 * @param ip
 * @param callback
 */
dns.reverse = function(ip, callback) {}

/**
 * The same as dns.resolve(), but only for mail exchange queries (MX
 * records).
 * @param domain
 * @param callback
 */
dns.resolveMx = function(domain, callback) {}

/**
 * The same as dns.resolve(), but only for text queries (TXT records).
 * @param domain
 * @param callback
 */
dns.resolveTxt = function(domain, callback) {}

/**
 * The same as dns.resolve(), but only for IPv4 queries (A records).
 * @param domain
 * @param callback
 */
dns.resolve4 = function(domain, callback) {}

/**
 * The same as dns.resolve(), but only for service records (SRV records).
 * @param domain
 * @param callback
 */
dns.resolveSrv = function(domain, callback) {}

/**
 * The same as dns.resolve4() except for IPv6 queries (an AAAA query).
 * @param domain
 * @param callback
 */
dns.resolve6 = function(domain, callback) {}

/**
 * Resolves a domain (e.g. 'google.com') into the first found A (IPv4) or
 * AAAA (IPv6) record.
 * @param domain
 * @param family
 * @param callback
 */
dns.lookup = function(domain, family, callback) {}

/**
 * The same as dns.resolve(), but only for canonical name records (CNAME
 * records). addresses is an array of the canonical name records available
 * for domain (e.g., ['bar.example.com']).
 * @param domain
 * @param callback
 */
dns.resolveCname = function(domain, callback) {}

/**
 * The same as dns.resolve(), but only for name server records (NS
 * records).
 * @param domain
 * @param callback
 */
dns.resolveNs = function(domain, callback) {}

exports = dns;

