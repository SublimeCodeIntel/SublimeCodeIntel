/**
 * Provides a few basic operating-system related utility functions.
 */
var os = {};

/**
 * Returns the system uptime in seconds.
 * @returns the system uptime in seconds
 */
os.uptime = function() {}

/**
 * Returns the total amount of system memory in bytes.
 * @returns the total amount of system memory in bytes
 */
os.totalmem = function() {}

/**
 * Returns the hostname of the operating system.
 * @returns the hostname of the operating system
 */
os.hostname = function() {}

/**
 * Returns an array of objects containing information about each CPU/core
 * installed: model, speed (in MHz), and times (an object containing the
 * number of CPU ticks spent in: user, nice, sys, idle, and irq).
 * @returns {Array} an array of objects containing information about each CPU/core installed: model, speed (in MHz), and times (an object containing the number of CPU ticks spent in: user, nice, sys, idle, and irq)
 */
os.cpus = function() {}

/**
 * Returns an array containing the 1, 5, and 15 minute load averages.
 * @returns an array containing the 1, 5, and 15 minute load averages
 */
os.loadavg = function() {}

/**
 * Returns the operating system release.
 * @returns the operating system release
 */
os.release = function() {}

/**
 * Returns the operating system name.
 * @returns the operating system name
 */
os.type = function() {}

/**
 * Returns the amount of free system memory in bytes.
 * @returns the amount of free system memory in bytes
 */
os.freemem = function() {}

/**
 * A constant defining the appropriate End-of-line marker for the operating
 * system.
 */
os.EOL = 0;

/**
 * Returns the operating system CPU architecture.
 * @returns the operating system CPU architecture
 */
os.arch = function() {}

/**
 * Get a list of network interfaces:
 */
os.networkInterfaces = function() {}

/**
 * Returns the operating system platform.
 * @returns the operating system platform
 */
os.platform = function() {}

/**
 * Returns the operating system's default directory for temp files.
 * @returns the operating system's default directory for temp files
 */
os.tmpDir = function() {}

exports = os;

