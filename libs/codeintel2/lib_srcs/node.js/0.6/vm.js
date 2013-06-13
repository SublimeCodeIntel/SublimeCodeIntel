/**
 * You can access this module with:
 */
var vm = {};

/**
 * createScript compiles code but does not run it. Instead, it returns a
 * vm.Script object representing this compiled code. This script can be run
 * later many times using methods below. The returned script is not bound
 * to any global object. It is bound before each run, just for that run.
 * filename is optional, it's only used in stack traces.
 * @param code
 * @param filename
 * @returns {vm.Script}
 */
vm.createScript = function(code, filename) {}

/**
 * vm.runInThisContext() compiles code, runs it and returns the result.
 * Running code does not have access to local scope. filename is optional,
 * it's used only in stack traces.
 * @param code
 * @param filename
 */
vm.runInThisContext = function(code, filename) {}

/**
 * vm.runInNewContext compiles code, then runs it in sandbox and returns
 * the result. Running code does not have access to local scope. The object
 * sandbox will be used as the global object for code.
 * @param code
 * @param sandbox
 * @param filename
 */
vm.runInNewContext = function(code, sandbox, filename) {}

/**
 * A class for running scripts. Returned by vm.createScript.
 * @constructor
 */
vm.Script = function() {}

/**
 * Similar to vm.runInThisContext but a method of a precompiled Script
 * object.
 */
vm.Script.prototype.runInThisContext = function() {}

/**
 * Similar to vm.runInNewContext a method of a precompiled Script object.
 * @param sandbox
 */
vm.Script.prototype.runInNewContext = function(sandbox) {}

/**
 * vm.createContext creates a new context which is suitable for use as the
 * 2nd argument of a subsequent call to vm.runInContext. A (V8) context
 * comprises a global object together with a set of build-in objects and
 * functions. The optional argument initSandbox will be shallow-copied to
 * seed the initial contents of the global object used by the context.
 * @param initSandbox
 */
vm.createContext = function(initSandbox) {}

/**
 * vm.runInContext compiles code, then runs it in context and returns the
 * result. A (V8) context comprises a global object, together with a set of
 * built-in objects and functions. Running code does not have access to
 * local scope and the global object held within context will be used as
 * the global object for code.
 * @param code
 * @param context
 * @param filename
 */
vm.runInContext = function(code, context, filename) {}

exports = vm;

