Change Log
----------

List of releases and changes, with the latest at the top:


v3.0.0 (unreleased, beta):

-   Uses CodeIntel as an OOP command and package. Needs to install
    CodeIntel with pip: pip install --upgrade --pre CodeIntel

v2.2.0 (2015-03-26):

-   Fixed issue with tabs and autocomplete

v2.1.9 (2015-03-21):

-   Fixed issue with codeintel\_enabled()

v2.1.8 (2015-03-18):

-   Fixed issue with is\_enabled()
-   Do not autocomplete on ENTER

v2.1.7 (2015-01-26):

-   Fixed triggering issues with autocompletion and stop chars.
-   ST2 improvements. Still might show "slow plugin" (just ignore,
    project\_file\_name is being emulated from ST3, which is "slow")
-   Cleanups

v2.1.6 (2015-01-23):

-   Optimizations.
-   Compatibility issues with ST2.
-   Stop characters fixed.

v2.1.5 (2015-01-22):

-   Cleanups.
-   Autocomplete also triggered after space (for import&lt;space&gt;
    autocompletions).
-   Tooltip and snippets for functions re-added.

v2.1.4 (2015-01-21):

-   Improved compatibility with ST2
-   PHP magic-methods tweaks ported from wizza-smile's fork.

v2.1.3 (2015-01-20):

-   Features and enhancements from wizza-smile's fork.
-   PHP completions within function brackets.

v2.1.2 (2015-01-16):

-   Fixed issue with ordereddict in ST3 (Python 3).
-   Fixed issue with unrevised languages.
-   Perl compatibility improved/fixed.

v2.1.1 (2015-01-14):

-   Currently, this version features all the new great enhancements by
    [wizza-smile](https://github.com/wizza-smile) which he is currently
    working on, in his own fork of SublimeCodeIntel: SublimeCodeIntel3
    at <https://github.com/wizza-smile/SublimeCodeIntel3>
-   Sublime Text 2 compatibility fixed.
-   Fix the "codeintel\_scan\_exclude\_dir" setting (it was doing
    nothing at all so far!).

v2.1.0 (2015-01-13):

-   New settings concept. Settings can now be defined in
    \*.sublime-project file.
-   Define the directory, where your projects codeintel database should
    reside (new setting "codeintel\_database\_dir").
-   Sublime style word completions from buffer (new setting
    "codeintel\_word\_completions" possible values: "buffer", "all" or
    "none").
-   Completions are now showing user-defined snippets.
-   PHP local variables support.
-   PHP static variables support.
-   PHP completions from HTML embedded blocks.
-   Improved speed for PHP completions dramatically by fixing the number
    of import libs.

v2.0.6 (2013-09-21):

-   Tooltips can use Popups, Output Panel or Status Bar ("popup",
    "panel", "status" respectively, in the settings)
-   Resolved issues with XML and other languages.
-   Improved speed by using cache for some things (added
    zope.cachedescriptors)

v2.0.5 (18-09-2013):

-   Resolved issues with ST2 in Mac OS X and Windows
-   Fixed a few problems with Ruby and HTML parsers in ST3

v2.0.4 (16-09-2013):

-   First non-pre-release for ST3

v2.0.3 (14-09-2013):

-   Libraries built for compatibility with more systems.

v2.0.2 (12-09-2013):

-   Initial Sublime Text 3 support!
-   OpenKomodo codebase updated to r13636
-   Snippets insertion delayed a bit.
-   Tooltips are removed when line changes.
-   Improved autocomplete in HTML.

v2.0.1 (19-07-2013):

-   Removed some Linux dependencies to GLIBC\_2.4.
-   Sublime Text 2 built-in auto complete no longer disabled by default
    (use "sublime\_auto\_complete": false setting instad).

v2.0 (11-07-2013):

-   SublimeCodeIntel's openkomodo codeintel engine updated. The new
    codeintel is faster and more reliable.
-   Sources have their own repositories at
    <http://github.com/SublimeCodeIntel>
-   Disables Sublime Text 2's auto\_complete by default (new
    `sublime_auto_complete` setting)
-   JavaScript and PHP: Do not include all files and directories from
    the project base directory while scanning.
-   JavaScript: Maximum directory depth is set to 2 (add explicit paths
    using javascriptExtraPaths).
-   PHP: Maximum directory depth is set to 5 (add explicit paths using
    phpExtraPaths).
-   Snippets for functions inserted during autocomplete.
-   Binary files for Linux, Windows and Mac OS X updated.
-   Shortcuts for jump to definition have changed.
-   PHP and UDL languages bugs fixed.
-   Stability improved (Should no longer use 100% CPU all the time.)

v1.4 (05-07-2013):

-   Added improved Package Control support and updated old versions.
-   Started transition to v2.0

v1.3 (20-12-2011):

-   This build should fix many of the problems seen in Linux systems.
-   Libraries for Linux rebuilt with libpcre statically (libpcre bundled
    for Linux builds).
-   `calltip()` is now thread safe (which caused some strange behavior
    in Linux where Sublime Text 2 ended up being unresponsive).

v1.2 (18-12-2011):

-   Added palette commands to disable/enable the plugin in many ways.
-   Added `codeintel_live_disabled_languages` and fixed `codeintel_live`
    to disable SublimeCodeIntel live autocomplete mode.
-   Support for new completion settings in Sublime Text 2 Build 2148.
-   JavaScript support improved (it's now much nicer with the CPU).
-   CSS files support much improved (thanks to Jon's new features in
    autocomplete).
-   Smarter language detection and fallbacks.
-   Improved autocomplete triggering, should now respond better.
