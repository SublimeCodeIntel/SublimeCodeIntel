/**
 * A single instance of Node runs in a single thread. To take advantage of
 * multi-core systems the user will sometimes want to launch a cluster of
 * Node processes to handle the load.
 */
var cluster = {};

/**
 * Spawn a new worker process. This can only be called from the master
 * process.
 */
cluster.fork = function() {}

/**
 * Boolean flags to determine if the current process is a master or a
 * worker process in a cluster. A process isMaster if
 * process.env.NODE_WORKER_ID is undefined.
 */
cluster.isMaster = 0;

/**
 * Boolean flags to determine if the current process is a master or a
 * worker process in a cluster. A process isMaster if
 * process.env.NODE_WORKER_ID is undefined.
 */
cluster.isWorker = 0;

exports = cluster;

