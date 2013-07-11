#!/usr/bin/env python2

import codeintel2.common
from codeintel2.common import EvalController
import logging
import cStringIO
import pprint

log = logging.getLogger("codeintel.oop.controller")


class OOPEvalController(EvalController):
    """Eval controller for out-of-process codeintel
    """

    have_errors = have_warnings = False
    silent = False

    def __init__(self, driver=None, request=None, *args, **kwargs):
        """Create an eval controller
        @param driver {Driver} The OOP driver instance to communicate via
        @param request {Request} The request causing the evaluation
        """
        log.debug("__init__")
        EvalController.__init__(self, *args, **kwargs)

        self.driver = driver
        self.request = request
        self.silent = request.get("silent", False)
        self.keep_existing = request.get("keep_existing", self.keep_existing)

        # Set up a logger to record any errors
        # Note that the output will be discarded if there it no error
        self.log_stream = cStringIO.StringIO()
        self.log_hndlr = logging.StreamHandler(self.log_stream)
        self.log = logging.getLogger("codeintel.evaluator")
        self.log.propagate = False
        self.log.addHandler(self.log_hndlr)
        self.best_msg = (0, "")

    def close(self):
        log.debug("close")
        EvalController.close(self)

    def set_desc(self, desc):
        log.debug("set_desc: %s", desc)
        EvalController.set_desc(self, desc)

        if not self.silent:
            self.log.error("error evaluating %s:\n  trigger: %s\n  log:",
                           desc, self.trg)
            # Reset the formatter to be minimal
            fmt = logging.Formatter(fmt="    %(levelname)s: %(message)s")
            self.log_hndlr.setFormatter(fmt)

    def setStatusMessage(self, msg, highlight):
        log.debug("setStatusMessage: %s, %s", msg, highlight)
        self.driver.send(request=self.request, success=None,
                         message=msg, highlight=highlight)

    def abort(self):
        log.debug("abort: %r", self.request)
        if self.is_aborted:
            # Controllers don't abort immediately; this is in the process of
            # aborting but hasn't finished yet
            log.debug("Suppressing repeat abort message: %r", self.request)
            return
        EvalController.abort(self)
        self.driver.fail(request=self.request, msg="aborted")

    def done(self, reason):
        log.debug("done: %s %s", reason,
                  "(aborted)" if self.is_aborted() else "")

        if self.cplns:
            # Report completions
            self.driver.send(cplns=self.cplns, request=self.request)
        elif self.calltips:
            self.driver.send(calltip=self.calltips[0], request=self.request)
        elif self.defns:
            # We can't exactly serialize blobs directly...
            def defn_serializer(defn):
                return defn.__dict__
            self.driver.send(defns=map(defn_serializer, self.defns or []),
                             request=self.request)
        elif self.is_aborted():
            pass  # already reported the abort
        elif self.silent:
            pass  # don't output any errors
        elif self.best_msg[0]:
            try:
                msg = "No %s found" % (self.desc,)
                if self.have_errors:
                    msg = self.best_msg[
                        1] + " (error determining %s)" % (self.desc,)
                    self.driver.report_error(self.log_stream.getvalue())
                elif self.have_warnings:
                    msg += "(warning: %s)" % (self.best_msg[1],)
            except TypeError as ex:
                # Guard against this common problem in log formatting above:
                #   TypeError: not enough arguments for format string
                log.exception(
                    "problem logging eval failure: self.log=%r", self.log_entries)
                msg = "error evaluating '%s'" % desc
            self.driver.fail(request=self.request, message=msg)

        self.log_stream.close()
        EvalController.done(self, reason)

    def setup_log(self):
        if not self.desc:
            desc = {codeintel2.common.TRG_FORM_CPLN: "completions",
                    codeintel2.common.TRG_FORM_CALLTIP: "calltip",
                    codeintel2.common.TRG_FORM_DEFN: "definition",
                    }.get(self.trg.form, "???")
            self.set_desc(desc)

    def debug(self, msg, *args):
        if self.silent:
            return
        self.setup_log()
        self.log.debug(msg, *args)
        if self.best_msg[0] < logging.DEBUG:
            self.best_msg = (logging.DEBUG, msg % args)

    def info(self, msg, *args):
        if self.silent:
            return
        self.setup_log()
        self.log.info(msg, *args)
        if self.best_msg[0] < logging.INFO:
            self.best_msg = (logging.INFO, msg % args)

    def warn(self, msg, *args):
        if self.silent:
            return
        self.setup_log()
        self.log.warn(msg, *args)
        if self.best_msg[0] < logging.WARN:
            self.best_msg = (logging.WARN, msg % args)
        self.have_warnings = True

    def error(self, msg, *args):
        if self.silent:
            return
        self.setup_log()
        self.log.error(msg, *args)
        if self.best_msg[0] < logging.ERROR:
            self.best_msg = (logging.ERROR, msg % args)
        self.have_errors = True
