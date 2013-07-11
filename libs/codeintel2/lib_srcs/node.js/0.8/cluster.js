/**
 * A single instance of Node runs in a single thread. To take advantage of
 * multi-core systems the user will sometimes want to launch a cluster of
 * Node processes to handle the load.
 * @base {events.EventEmitter}
 */
var cluster = {};

/**
 * The setupMaster is used to change the default 'fork' behavior. It takes
 * one option object argument.
 * @param settings {Object}
 */
cluster.setupMaster = function(settings) {}

/**
 * Spawn a new worker process. This can only be called from the master
 * process.
 * @param env {Object}
 */
cluster.fork = function(env) {}

/**
 * When calling this method, all workers will commit a graceful suicide.
 * When they are disconnected all internal handlers will be closed,
 * allowing the master process to die graceful if no other event is
 * waiting.
 * @param callback {Function}
 */
cluster.disconnect = function(callback) {}

/**
 * A Worker object contains all public information and method about a
 * worker.
 * @constructor
 */
cluster.Worker = function() {}
cluster.Worker.prototype = new events.EventEmitter();

/**
 * This function is equal to the send methods provided by
 * child_process.fork(). In the master you should use this function to send
 * a message to a specific worker. However in a worker you can also use
 * process.send(message), since this is the same function.
 * @param message {Object}
 * @param sendHandle {Handle}
 */
cluster.Worker.prototype.send = function(message, sendHandle) {}

/**
 * This function will kill the worker, and inform the master to not spawn a
 * new worker. The boolean suicide lets you distinguish between voluntary
 * and accidental exit.
 */
cluster.Worker.prototype.destroy = function() {}

/**
 * When calling this function the worker will no longer accept new
 * connections, but they will be handled by any other listening worker.
 * Existing connection will be allowed to exit as usual. When no more
 * connections exist, the IPC channel to the worker will close allowing it
 * to die graceful. When the IPC channel is closed the disconnect event
 * will emit, this is then followed by the exit event, there is emitted
 * when the worker finally die.
 */
cluster.Worker.prototype.disconnect = function() {}

/**
 * Each new worker is given its own unique id, this id is stored in the id.
 */
cluster.Worker.prototype.id = 0;

/**
 * All workers are created using child_process.fork(), the returned object
 * from this function is stored in process.
 */
cluster.Worker.prototype.process = 0;

/**
 * This property is a boolean. It is set when a worker dies after calling
 * .destroy() or immediately after calling the .disconnect() method. Until
 * then it is undefined.
 */
cluster.Worker.prototype.suicide = 0;

/** @__local__ */ cluster.Worker.__events__ = {};

/**
 * This event is the same as the one provided by child_process.fork(). In
 * the master you should use this event, however in a worker you can also
 * use process.on('message') As an example, here is a cluster that keeps
 * count of the number of requests in the master process using the message
 * system:
 */
cluster.Worker.__events__.message = function() {};

/**
 * Same as the cluster.on('online') event, but emits only when the state
 * change on the specified worker.
 */
cluster.Worker.__events__.online = function() {};

/**
 * Same as the cluster.on('listening') event, but emits only when the state
 * change on the specified worker.
 */
cluster.Worker.__events__.listening = function() {};

/**
 * Same as the cluster.on('disconnect') event, but emits only when the
 * state change on the specified worker.
 */
cluster.Worker.__events__.disconnect = function() {};

/**
 * Emitted by the individual worker instance, when the underlying child
 * process is terminated. See child_process event: 'exit'.
 */
cluster.Worker.__events__.exit = function() {};

/**
 * All settings set by the .setupMaster is stored in this settings object.
 */
cluster.settings = 0;

/**
 * True if the process is a master. This is determined by the
 * process.env.NODE_UNIQUE_ID. If process.env.NODE_UNIQUE_ID is undefined,
 * then isMaster is true.
 */
cluster.isMaster = 0;

/**
 * This boolean flag is true if the process is a worker forked from a
 * master.
 */
cluster.isWorker = 0;

/**
 * All settings set by the .setupMaster is stored in this settings object.
 */
cluster.settings = 0;

/**
 * In the cluster all living worker objects are stored in this object by
 * there id as the key. This makes it easy to loop through all living
 * workers.
 */
cluster.workers = 0;

var events = require('events');

exports = cluster;

