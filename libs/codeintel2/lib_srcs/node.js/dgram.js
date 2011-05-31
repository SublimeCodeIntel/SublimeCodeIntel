/**
 * Datagram sockets are available through require('dgram'). Datagrams are
 * most commonly handled as IP/UDP messages but they can also be used over
 * Unix domain sockets.
 */
var dgram = {};

/**
 * Creates a datagram socket of the specified types. Valid types are: udp4,
 * udp6, and unix_dgram.
 * @returns dgram.Socket
 */
dgram.createSocket = function() {}

dgram.Socket = function() {}
dgram.Socket.prototype = {}
/**
 * Tells the kernel to join a multicast group with IP_ADD_MEMBERSHIP socket
 * option.
 */
dgram.Socket.prototype.addMembership = function() {}
/**
 * For UDP sockets, listen for datagrams on a named port and optional
 * address. If address is not specified, the OS will try to listen on all
 * addresses.
 */
dgram.Socket.prototype.bind = function() {}
/**
 * Sets the IP_MULTICAST_TTL socket option. TTL stands for "Time to Live,"
 * but in this context it specifies the number of IP hops that a packet is
 * allowed to go through, specifically for multicast traffic. Each router
 * or gateway that forwards a packet decrements the TTL. If the TTL is
 * decremented to 0 by a router, it will not be forwarded.
 */
dgram.Socket.prototype.setMulticastTTL = function() {}
/**
 * For UDP sockets, the destination port and IP address must be specified.
 * A string may be supplied for the address parameter, and it will be
 * resolved with DNS. An optional callback may be specified to detect any
 * DNS errors and when buf may be re-used. Note that DNS lookups will delay
 * the time that a send takes place, at least until the next tick. The only
 * way to know for sure that a send has taken place is to use the callback.
 */
dgram.Socket.prototype.send = function() {}
/**
 * Sets or clears the IP_MULTICAST_LOOP socket option. When this option is
 * set, multicast packets will also be received on the local interface.
 */
dgram.Socket.prototype.setMulticastLoopback = function() {}
/**
 * Sets the IP_TTL socket option. TTL stands for "Time to Live," but in
 * this context it specifies the number of IP hops that a packet is allowed
 * to go through. Each router or gateway that forwards a packet decrements
 * the TTL. If the TTL is decremented to 0 by a router, it will not be
 * forwarded. Changing TTL values is typically done for network probes or
 * when multicasting.
 */
dgram.Socket.prototype.setTTL = function() {}
/**
 * Sets or clears the SO_BROADCAST socket option. When this option is set,
 * UDP packets may be sent to a local interface's broadcast address.
 */
dgram.Socket.prototype.setBroadcast = function() {}
/**
 * Returns an object containing the address information for a socket. For
 * UDP sockets, this object will contain address and port. For Unix domain
 * sockets, it will contain only address.
 */
dgram.Socket.prototype.address = function() {}
/**
 * Close the underlying socket and stop listening for data on it. UDP
 * sockets automatically listen for messages, even if they did not call
 * bind().
 */
dgram.Socket.prototype.close = function() {}
/**
 * Opposite of addMembership - tells the kernel to leave a multicast group
 * with IP_DROP_MEMBERSHIP socket option. This is automatically called by
 * the kernel when the socket is closed or process terminates, so most apps
 * will never need to call this.
 */
dgram.Socket.prototype.dropMembership = function() {}


exports = dgram;

