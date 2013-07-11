#!python
# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
# License for the specific language governing rights and limitations
# under the License.
#
# The Original Code is Komodo code.
#
# The Initial Developer of the Original Code is ActiveState Software Inc.
# Portions created by ActiveState Software Inc are Copyright (C) 2000-2007
# ActiveState Software Inc. All Rights Reserved.
#
# Contributor(s):
#   ActiveState Software Inc
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****

"""The codeintel indexer is a thread that handles scanning files and
loading them into the database. There is generally one indexer on the
Manager instance.

    mgr.idxr = Indexer(mgr)

XXX A separate indexer instance may be used for batch updates of the db.
"""
# TODO:
# - How are scan errors handled? do we try to keep from re-scanning over
#   and over? Perhaps still use mtime to only try again on new content.
#   Could still have a "N strikes in the last 1 minute" rule or
#   something.
# - batch updating (still wanted? probably)

import os
import sys
import threading
import time
import bisect
import Queue
from hashlib import md5
import traceback

import logging

from codeintel2.common import *
from codeintel2.buffer import Buffer
from codeintel2.database.langlib import LangDirsLib
from codeintel2.database.multilanglib import MultiLangDirsLib

if _xpcom_:
    from xpcom.server import UnwrapObject


#---- globals
log = logging.getLogger("codeintel.indexer")
# log.setLevel(logging.DEBUG)


#---- internal support
class _PriorityQueue(Queue.Queue):
    """A thread-safe priority queue.

    In order to use this the inserted items should be tuples with the
    priority first. Note that subsequent elements of the item tuples will
    be used for secondary sorting. As a result, it is often desirable to
    make the second tuple index be a timestamp so that the queue is a
    FIFO for elements with the same priority, e.g.:
        item = (PRIORITY, time.time(), element)

    Usage:
        q = _PriorityQueue(0)  # unbounded queue
        q.put( (2, time.time(), "second") )
        q.put( (1, time.time(), "first") )
        q.put( (3, time.time(), "third") )
        priority, timestamp, value = q.get()
    """
    def _put(self, item):
        bisect.insort(self.queue, item)

    # The following are to ensure a *list* is being used as the internal
    # Queue data structure. Python 2.4 switched to using a deque
    # internally which doesn't have the insert() method that
    # bisect.insort() uses.
    def _init(self, maxsize):
        self.maxsize = maxsize
        self.queue = []

    def _get(self):
        return self.queue.pop(0)


class _Request(object):
    """Base class for a queue-able thing.

    A request object must have an 'id'. This is used for "staging"
    requests on the queue. A staged request will sit around for 'delay'
    amount of time before actually being put on the processing queue.
    During that wait, a subsequent stage request with the same 'id' will
    replace the first one -- including resetting the delay. This is
    useful for staging relatively expensive processing in the background
    for content that is under ongoing changes (e.g. for processing an
    editor buffer while it is being editted).
    """
    # XXX PERF: use a slot?
    id = None

    def __init__(self, id=None):
        if id is not None:
            self.id = id


class _UniqueRequestPriorityQueue(_PriorityQueue):
    """A thread-safe priority queue for '_Request' objects.

    This queue class extends _PriorityQueue with the condition that:
    When adding a _Request to the queue, if a _Request with the same id
    already exists in the queue, then the new _Request inherits the
    higher priority and the earlier timestamp of the two and _replaces_
    the older _Request.

    This condition is added because there is no point in scanning file
    contents from time T1 when a scan of the file contents at time T2
    (more recent) is being requested. It is important to adopt the
    higher priority (and earlier timestamp) to ensure the requestor does
    not starve.

    Note: This presumes that an "item" is this 3-tuple:
        (<priority-number>, <timestamp>, <_Request instance>)
    """
    def __init__(self, maxsize=0):
        _PriorityQueue.__init__(self, maxsize)
        self._item_from_id = {}

    def _put(self, item):
        # Remove a possible existing request for the same file (there can
        # be only one).
        priority, timestamp, request = item
        id = request.id
        if id in self._item_from_id:
            i = self._item_from_id[id]
            self.queue.remove(i)
            p, t, r = i
            item = (min(priority, p), t, request)
        # Add the (possibly updated) item to the queue.
        self._item_from_id[id] = item
        _PriorityQueue._put(self, item)

    def _get(self):
        item = _PriorityQueue._get(self)
        del self._item_from_id[item[-1].id]
        return item


class _StagingRequestQueue(_UniqueRequestPriorityQueue):
    """A thread-safe priority queue for '_Request' objects with delayed
    staging support.

    This queue class extends _UniqueRequestPriorityQueue by adding the
    .stage() method. This method is like the regular .put() method
    except that staged requests are only actually placed on the queue if
    a certain period of inactivity passes without subsequent stage
    requests for the same request id.

    This is to support reasonable performance for live updating while a
    document is being edited. Rather than executing a scan for every
    intermediate edited state, scanning is only  after a period of
    relative inactivity.

    One additional burden is that a "staging thread" is involved so one must
    call this queue's .finalize() method to properly shut it down.

    As with the _ScanRequestQueue this queue presumes that and item is this
    3-tuple:
            (<priority-number>, <timestamp>, <ScanRequest instance>)
    """
    DEFAULT_STAGING_DELAY = 1.5  # default delay from on deck -> on queue (s)

    def __init__(self, maxsize=0, stagingDelay=None):
        """Create a staging scan request queue.

            "maxsize" (optional) is an upperbound limit on the number of
                items in the queue (<= 0 means the queue is unbounded).
            "stagingDelay" (optional) is a number of seconds to use as a
                delay from being staged to being placed on the queue.
        """
        _UniqueRequestPriorityQueue.__init__(self, maxsize)
        if stagingDelay is None:
            self._stagingDelay = self.DEFAULT_STAGING_DELAY
        else:
            self._stagingDelay = stagingDelay
        self._onDeck = {
            # <request-id> : (<time when due>, <priority>, <queue item>)
        }
        self._nothingOnDeck = threading.Lock()
        self._nothingOnDeck.acquire()
        self._terminate = 0  # boolean telling "staging thread" to terminate
        self._stager = threading.Thread(target=self._stagingThread,
                                        name="request staging thread")
        self._stager.setDaemon(True)
        self._stager.start()

    def finalize(self):
        if self._stager:
            self._terminate = 1
            # Make sure staging thread isn't blocked so it can terminate.
            self.mutex.acquire()
            try:
                if not self._onDeck:
                    self._nothingOnDeck.release()
            finally:
                self.mutex.release()
            # Don't bother join'ing because there is no point waiting for
            # up to self._stagingDelay while the staging thread shuts down.
            # self._stager.join()

    def stage(self, item, delay=None):
        if delay is None:
            delay = self._stagingDelay
        self.mutex.acquire()
        try:
            priority, timestamp, request = item
            wasEmpty = not self._onDeck
            if request.id not in self._onDeck \
               or self._onDeck[request.id][1] != PRIORITY_IMMEDIATE:
                self._onDeck[request.id] = (timestamp + delay, priority, item)
                if wasEmpty:
                    self._nothingOnDeck.release()
        finally:
            self.mutex.release()

    def _stagingThread(self):
        """Thread that handles moving requests on-deck to the queue."""
        log.debug("staging thread: start")
        while 1:
            # If nothing is on-deck, wait until there is.
            # log.debug("staging thread: acquire self._nothingOnDeck")
            self._nothingOnDeck.acquire()
            # log.debug("staging thread: acquired self._nothingOnDeck")
            if self._terminate:
                break

            # Place any "due" items on the queue.
            self.mutex.acquire()
            somethingStillOnDeck = 1
            currTime = time.time()
            toQueue = []
            try:
                for id, (timeDue, priority, item) in self._onDeck.items():
                    if currTime >= timeDue:
                        toQueue.append(item)
                        del self._onDeck[id]
                if not self._onDeck:
                    somethingStillOnDeck = 0
            finally:
                if somethingStillOnDeck:
                    self._nothingOnDeck.release()
                self.mutex.release()
            if toQueue:
                log.debug("staging thread: queuing %r", toQueue)
                for item in toQueue:
                    self.put(item)

            # Sleep for a bit.
            # XXX If the latency it too large we may want to sleep for some
            #    fraction of the staging delay.
            log.debug("staging thread: sleep for %.3fs", self._stagingDelay)
            time.sleep(self._stagingDelay)
        log.debug("staging thread: end")


#---- public classes
class XMLParseRequest(_Request):
    """A request to re-parse and XML-y/HTML-y file

    (For XML completion and Komodo's DOMViewer.)
    """
    def __init__(self, buf, priority, force=False):
        if _xpcom_:
            buf = UnwrapObject(buf)
        self.buf = buf
        self.id = buf.path + "#xml-parse"
        self.priority = priority
        self.force = force

    def __repr__(self):
        return "<XMLParseRequest %r>" % self.id

    def __str__(self):
        return "xml parse '%s' (prio %s)" % (self.buf.path, self.priority)


class ScanRequest(_Request):
    """A request to scan a file for codeintel.

    A ScanRequest has the following properties:
        "buf" is the CitadelBuffer instance.
        "priority" must be one of the PRIORITY_* priorities.
        "force" is a boolean indicating if a scan should be run even if
            the database is already up-to-date for this content.
        "mtime" is the modified time of the file/content. If not given
            it defaults to the current time.
        "on_complete" (optional) is a callable to call when the scan
            and load is complete. (XXX: Is this being used by anyone?)

        "status" is set on completion. See .complete() docstring for details.
    """
    status = None

    def __init__(self, buf, priority, force=False, mtime=None, on_complete=None):
        if _xpcom_:
            buf = UnwrapObject(buf)
        self.buf = buf
        self.id = buf.path
        self.priority = priority
        self.force = force
        if mtime is None:
            self.mtime = time.time()
        else:
            self.mtime = mtime
        self.on_complete = on_complete
        self.complete_event = threading.Event()  # XXX use a pool

    def __repr__(self):
        return "<ScanRequest %r>" % self.id

    def __str__(self):
        return "scan request '%s' (prio %s)" % (self.buf.path, self.priority)

    def complete(self, status):
        """Called by scheduler when this scan is complete (whether or
        not it was successful/skipped/whatever).

            "status" is one of the following:
                changed     The scan was done and (presumably) something
                            changed. PERF: Eventually want to be able to
                            detect when an actual change is made to be
                            used elsewhere to know not to update.
                skipped     The scan was skipped.
        """
        log.debug("complete %s", self)
        self.status = status
        self.complete_event.set()
        if self.on_complete:
            try:
                self.on_complete()
            except:
                log.exception("ignoring exception in ScanRequest "
                              "on_complete callback")

    def wait(self, timeout=None):
        """Can be called by code requesting a scan to wait for completion
        of this particular scan.
        """
        self.complete_event.wait(timeout)


class PreloadBufLibsRequest(_Request):
    priority = PRIORITY_BACKGROUND

    def __init__(self, buf):
        if _xpcom_:
            buf = UnwrapObject(buf)
        self.buf = buf
        self.id = buf.path + "#preload-libs"

    def __repr__(self):
        return "<PreloadBufLibsRequest %r>" % self.id

    def __str__(self):
        return "pre-load libs for '%s'" % self.buf.path


class PreloadLibRequest(_Request):
    priority = PRIORITY_BACKGROUND

    def __init__(self, lib):
        self.lib = lib
        self.id = "%s %s with %s dirs#preload-lib" \
                  % (lib.lang, lib.name, len(lib.dirs))

    def __repr__(self):
        return "<PreloadLibRequest %r>" % self.id

    def __str__(self):
        return "pre-load %s %s (%d dirs)" \
               % (self.lib.lang, self.lib.name, len(self.lib.dirs))


class CullMemRequest(_Request):
    id = "cull memory request"
    priority = PRIORITY_BACKGROUND


class IndexerStopRequest(_Request):
    id = "indexer stop request"
    priority = PRIORITY_CONTROL

    def __repr__(self):
        return '<'+self.id+'>'


class IndexerPauseRequest(_Request):
    id = "indexer pause request"
    priority = PRIORITY_CONTROL

    def __repr__(self):
        return '<'+self.id+'>'


class Indexer(threading.Thread):
    """A codeintel indexer thread.

    An indexer is mainly responsible for taking requests to scan
    (Citadel) buffers and load the data into the appropriate LangZone of
    the database.

#XXX Only needed when/if batch updating is redone.
##    This thread manages a queue of ScanRequest's, scheduling the scans in
##    priority order. It has two modes of usage:
##        MODE_DAEMON
##            The scheduler remains running until it is explicitly stopped with
##            the .stop() method.
##        MODE_ONE_SHOT
##            All added requests are processed and then the scheduler
##            terminates. Note that the .stageRequest() method is not
##            allowed in this mode.

    Usage:
        from codeintel.indexer import Indexer
        idxr = Indexer(mgr)
        idxr.start()
        try:
            # idxr.stage_request(<request>)
            # idxr.add_request(<request>)
        finally:
            idxr.finalize()

    Dev Notes:
    - The intention is the indexer will grow to handle other requests as
      well (saving and culling cached parts of the database).
    - There is a potential race condition on request id generation
      if addRequest/stageRequest calls are made from multiple threads.
    """
    MODE_DAEMON, MODE_ONE_SHOT = range(2)
    mode = MODE_DAEMON

    class StopIndexing(Exception):
        """Used to signal that indexer iteration should stop.

        Dev Note: I *could* use StopIteration here, but I don't want to
        possibly misinterpret a real StopIteration.
        """
        pass

    def __init__(self, mgr, on_scan_complete=None):
        """
            "on_scan_complete" (optional), if specified, is called when
                a ScanRequest is completed.

        TODO: add back the requestStartCB and completedCB (for batch updates)
        """
        threading.Thread.__init__(self, name="codeintel indexer")
        self.setDaemon(True)
        self.mgr = mgr
        self.on_scan_complete = on_scan_complete
        if self.mode == self.MODE_DAEMON:
            self._requests = _StagingRequestQueue()
        else:
            self._requests = _UniqueRequestPriorityQueue()
        self._stopping = False
        self._resumeEvent = None

    def finalize(self):
        """Shutdown the indexer.

        This must be done even if the the indexer thread was never
        .start()'ed -- because of the thread used for the
        _StagingRequestQueue.
        """
        self._stopping = True
        if isinstance(self._requests, _StagingRequestQueue):
            self._requests.finalize()
        if self.isAlive():
            self.add_request(IndexerStopRequest())
            try:
                self.join(5)  # see bug 77284
            except AssertionError:
                pass  # thread was not started

    def pause(self):
        self._resumeEvent = threading.Event()
        self._pauseEvent = threading.Event()
        # TODO: shouldn't this be `self.add_request`?
        self.addRequest(IndexerPauseRequest())
        self._pauseEvent.wait()  # wait until the Scheduler is actually paused
        log.debug("indexer: paused")

    def resume(self):
        if self._resumeEvent:
            self._resumeEvent.set()
            self._resumeEvent = None
        log.debug("indexer: resumed")

    def stage_request(self, request, delay=None):
        log.debug("stage %r", request)
        if self.mode == self.MODE_ONE_SHOT:
            raise CodeIntelError("cannot call stage requests on a "
                                 "MODE_ONE_SHOT indexer")
        # self._abortMatchingRunner(request.buf.path, request.buf.lang)
        self._requests.stage((request.priority, time.time(), request), delay)

    def add_request(self, request):
        log.debug("add %r", request)
        # self._abortMatchingRunner(request.buf.path, request.buf.lang)
        self._requests.put((request.priority, time.time(), request))

# XXX re-instate for batch updating (was getNumRequests)
##    def num_requests(self):
##        return self._requests.qsize()

    def run(self):    # the scheduler thread run-time
        log.debug("indexer: start")
##        reason = "failed"
        try:
            while 1:
                try:
                    self._iteration()
                except Queue.Empty:  # for mode=MODE_ONE_SHOT only
##                    reason = "completed"
                    break
                except self.StopIndexing:
##                    reason = "stopped"
                    break
                except:
                    # Because we aren't fully waiting for indexer
                    # termination in `self.finalize` it is possible that
                    # an ongoing request fails (Manager finalization
                    # destroys the `mgr.db` instance). Don't bother
                    # logging an error if we are stopping.
                    #
                    # Note: The typical culprit is a *long*
                    # <PreloadBufLibsRequest> for a PHP or JS library
                    # dir. Ideally this would be split into a number of
                    # lower-prio indexer requests.
                    if not self._stopping:
                        log.exception("unexpected internal error in indexer: "
                                      "ignoring and continuing")
        finally:
##            try:
##                if self._completedCB:
##                    self._completedCB(reason)
##            except:
##                log.exception("unexpected error in completion callback")
            log.debug("indexer thread: stopped")

    def _iteration(self):
        """Handle one request on the queue.

        Raises StopIndexing exception if iteration should stop.
        """
        # log.debug("indexer: get request")
        if self.mode == self.MODE_DAEMON:
            priority, timestamp, request = self._requests.get()
        else:  # mode == self.MODE_ONE_SHOT
            priority, timestamp, request = self._requests.get_nowait()
        # log.debug("indexer: GOT request")

        try:
            if request.priority == PRIORITY_CONTROL:  # sentinel
                if isinstance(request, IndexerStopRequest):
                    raise self.StopIndexing()
                elif isinstance(request, IndexerPauseRequest):
                    self._pauseEvent.set(
                    )  # tell .pause() that Indexer has paused
                    self._resumeEvent.wait()
                    return
                else:
                    raise CodeIntelError("unexpected indexer control "
                                         "request: %r" % request)

            if isinstance(request, ScanRequest):
                # Drop this request if the database is already up-to-date.
                db = self.mgr.db
                buf = request.buf
                status = "changed"
                if not request.force:
                    scan_time_in_db = db.get_buf_scan_time(buf)
                    if scan_time_in_db is not None \
                       and scan_time_in_db > request.mtime:
                        log.debug("indexer: drop %s: have up-to-date data for "
                                  "%s in the db", request, buf)
                        status = "skipped"
                        return

                buf.scan(mtime=request.mtime)

            elif isinstance(request, XMLParseRequest):
                request.buf.xml_parse()

            elif isinstance(request, CullMemRequest):
                log.debug("cull memory requested")
                self.mgr.db.cull_mem()

            # Currently these two are somewhat of a DB zone-specific hack.
            # TODO: The standard DB "lib" iface should grow a
            #      .preload() (and perhaps .can_preload()) with a
            #      ctlr arg. This should be unified with the current
            #      StdLib.preload().
            elif isinstance(request, PreloadBufLibsRequest):
                for lib in request.buf.libs:
                    if isinstance(lib, (LangDirsLib, MultiLangDirsLib)):
                        lib.ensure_all_dirs_scanned()
            elif isinstance(request, PreloadLibRequest):
                lib = request.lib
                assert isinstance(lib, (LangDirsLib, MultiLangDirsLib))
                lib.ensure_all_dirs_scanned()

            if not isinstance(request, CullMemRequest) and self.mode == self.MODE_DAEMON:
                # we did something; ask for a memory cull after 5 minutes
                log.debug("staging new cull mem request")
                self.stage_request(CullMemRequest(), 300)
            self.mgr.db.report_event(None)

        finally:
            if isinstance(request, ScanRequest):
                request.complete(status)
                if self.on_scan_complete:
                    try:
                        self.on_scan_complete(request)
                    except:
                        log.exception("ignoring exception in Indexer "
                                      "on_scan_complete callback")


#---- internal support stuff
# Recipe: indent (0.2.1) in C:\trentm\tm\recipes\cookbook
def _indent(s, width=4, skip_first_line=False):
    """_indent(s, [width=4]) -> 's' indented by 'width' spaces

    The optional "skip_first_line" argument is a boolean (default False)
    indicating if the first line should NOT be indented.
    """
    lines = s.splitlines(1)
    indentstr = ' '*width
    if skip_first_line:
        return indentstr.join(lines)
    else:
        return indentstr + indentstr.join(lines)
