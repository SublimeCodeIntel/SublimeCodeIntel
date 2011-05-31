/**
 * You can access this module with:
 */
var vm = {};

/**
 * createScript compiles code as if it were loaded from filename, but does
 * not run it. Instead, it returns a vm.Script object representing this
 * compiled code. This script can be run later many times using methods
 * below. The returned script is not bound to any global object. It is
 * bound before each run, just for that run. filename is optional.
 * @return vm.Script
 */
vm.createScript = function() {}

/**
 * vm.runInThisContext() compiles code as if it were loaded from filename,
 * runs it and returns the result. Running code does not have access to
 * local scope. filename is optional.
 */
vm.runInThisContext = function() {}

/**
 * vm.runInNewContext compiles code to run in sandbox as if it were loaded
 * from filename, then runs it and returns the result. Running code does
 * not have access to local scope and the object sandbox will be used as
 * the global object for code. sandbox and filename are optional.
 */
vm.runInNewContext = function() {}

vm.Script = function() {}
vm.Script.prototype = {}
/**
 * Similar to vm.runInThisContext but a method of a precompiled Script
 * object. script.runInThisContext runs the code of script and returns the
 * result. Running code does not have access to local scope, but does have
 * access to the global object (v8: in actual context).
 */
vm.Script.prototype.runInThisContext = function() {}
/**
 * Similar to vm.runInNewContext a method of a precompiled Script object.
 * script.runInNewContext runs the code of script with sandbox as the
 * global object and returns the result. Running code does not have access
 * to local scope. sandbox is optional.
 */
vm.Script.prototype.runInNewContext = function() {}


exports = vm;

