SublimeCodeIntel
================

Code intelligence plugin ported from `Open Komodo Editor <http://www.openkomodo.com/>`_ to `Sublime Text 2 <http://www.sublimetext.com/2>`_.

Supports all the languages Komodo Editor supports for Code Intelligence (CIX, CodeIntel2):

    JavaScript, Mason, XBL, XUL, RHTML, SCSS, Python, HTML, Ruby, Python3, XML, Sass, XSLT, Django, HTML5, Perl, CSS, Twig, Less, Smarty, Node.js, Tcl, TemplateToolkit, PHP.

Provides the following features:

* Jump to Symbol Definition - Jump to the file and line of the definition of a symbol.
* Imports autocomplete - Shows autocomplete with the available modules/symbols in real time.
* Function Call tooltips - Displays information in the status bar about the working function.

Plugin should work in all three platforms (MacOS X, Windows and Linux).

.. image:: http://pledgie.com/campaigns/16511.png?skin_name=chrome
   :alt: Click here to lend your support to SublimeCodeIntel and make a donation at pledgie.com!
   :target: http://pledgie.com/campaigns/16511


Installing
----------
**With the Package Control plugin:** The easiest way to install SublimeCodeIntel is through Package Control, which can be found at this site: http://wbond.net/sublime_packages/package_control

Once you install Package Control, restart ST2 and bring up the Command Palette (``Command+Shift+P`` on OS X, ``Control+Shift+P`` on Linux/Windows). Select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select SublimeCodeIntel when the list appears. The advantage of using this method is that Package Control will automatically keep SublimeCodeIntel up to date with the latest version.

**Without Git:** Download the latest source from `GitHub <http://github.com/SublimeCodeIntel/SublimeCodeIntel>`_ and copy the whole directory into the Packages directory.

**With Git:** Clone the repository in your Sublime Text 2 Packages directory, located somewhere in user's "Home" directory::

    git clone git://github.com/SublimeCodeIntel/SublimeCodeIntel.git


The "Packages" packages directory is located at:

* OS X::

    ~/Library/Application Support/Sublime Text 2/Packages/

* Linux::

    ~/.Sublime Text 2/Packages/

* Windows::

    %APPDATA%/Sublime Text 2/Packages/


Using
-----

* Start typing code as usual, autocomplete will pop up whenever it's available. SublimeCodeIntel will also allow you to jump around symbol definitions even across files with just a click ..and back.

  For Mac OS X:
    * Jump to definition = ``Control+Click``
    * Jump to definition = ``Control+Command+Alt+Up``
    * Go back = ``Control+Command+Alt+Left``
    * Manual Code Intelligence = ``Control+Shift+space``

  For Linux:
    * Jump to definition = ``Super+Click``
    * Jump to definition = ``Control+Super+Alt+Up``
    * Go back = ``Control+Super+Alt+Left``
    * Manual Code Intelligence = ``Control+Shift+space``

  For Windows:
    * Jump to definition = ``Alt+Click``
    * Jump to definition = ``Control+Windows+Alt+Up``
    * Go back = ``Control+Windows+Alt+Left``
    * Manual Code Intelligence = ``Control+Shift+space``

Don't despair! The first time you use it it needs to build some indexes and it can take more than a few seconds.

It just works!


Configuring
-----------
For adding additional library paths (django and extra libs paths for Python or extra paths to look for .js files for JavaScript for example), either add those paths as folders to your project, or create an optional codeintel configuration file in your home or in your project's root.

Configuration files (``~/.codeintel/config`` or ``project_root/.codeintel/config``). All configurations are optional. Example::

    {
        "PHP": {
            "php": '/usr/bin/php',
            "phpExtraPaths": [],
            "phpConfigFile": 'php.ini'
        },
        "JavaScript": {
            "javascriptExtraPaths": []
        },
        "Perl": {
            "perl": "/usr/bin/perl",
            "perlExtraPaths": []
        },
        "Ruby": {
            "ruby": "/usr/bin/ruby",
            "rubyExtraPaths": []
        },
        "Python": {
            "python": '/usr/bin/python',
            "pythonExtraPaths": []
        },
        "Python3": {
            "python": '/usr/bin/python3',
            "pythonExtraPaths": []
        }
    }

Additional settings can be configured in the User File Settings:

* A list of disabled languages can be set using "codeintel_disabled_languages". Ex. ``"codeintel_disabled_languages": ['css']``

* Live autocomplete can be disabled by setting "codeintel_live" to false.

* Live autocompletion can be disabled in a per-language basis, using "codeintel_live_disabled_languages". Ex. ``"codeintel_live_disabled_languages": ['css']``

* Information for more settings is available in the ``Base File.sublime-settings`` file.


Troubleshooting
---------------

To force re-indexation of the code intelligence database you need to follow these steps:

* Close Sublime Text 2

* Open a terminal or navigate through your directories to find the directory ``~/.codeintel`` that contains ``codeintel.log``, ``VERSION`` and the directory ``db``. In Windows, this should be at ``%userprofile%\.codeintel``.

* Delete the whole directory ``~/.codeintel`` and all of its content. Particularly, if you want to delete only the indexes, the code intelligence database indexes are located inside ``~/.codeintel/db``.

* Start Sublime Text 2 and enjoy a clean re-indexing!


Building
--------

Building process is no longer distributed with this repository. You need to get SublimeCodeIntel/`CodeIntelSources <https://github.com/SublimeCodeIntel/CodeIntelSources/>`_ to run ``build.sh``.

More information in SublimeCodeIntel/CodeIntelSources/`src <https://github.com/SublimeCodeIntel/CodeIntelSources/src>`_.


What's New
----------
v2.0.1 (19-07-2013):

- Removed some Linux dependencies to GLIBC_2.4.

- Sublime Text 2 built-in auto complete no longer disabled by default (use `"sublime_auto_complete": false` setting instad).


v2.0 (11-07-2013):

+ SublimeCodeIntel's openkomodo codeintel engine updated. The new codeintel is faster and more reliable.

+ Sources have their own repositories at http://github.com/SublimeCodeIntel

- Disables Sublime Text 2's auto_complete by default (new ``sublime_auto_complete`` setting)

- JavaScript and PHP: Do not include all files and directories from the project base directory while scanning.

- JavaScript: Maximum directory depth is set to 2 (add explicit paths using javascriptExtraPaths).

- PHP: Maximum directory depth is set to 5 (add explicit paths using phpExtraPaths).

+ Snippets for functions inserted during autocomplete.

+ Binary files for Linux, Windows and Mac OS X updated.

+ Shortcuts for jump to definition have changed.

- PHP and UDL languages bugs fixed.

- Stability improved (Should no longer use 100% CPU all the time.)


v1.4 (05-07-2013):

+ Added improved Package Control support and updated old versions.

+ Started transition to v2.0


v1.3 (20-12-2011):

+ This build should fix many of the problems seen in Linux systems.

- Libraries for Linux rebuilt with libpcre statically (libpcre bundled for Linux builds).

- ``calltip()`` is now thread safe (which caused some strange behavior in Linux
  where Sublime Text 2 ended up being unresponsive).


v1.2 (18-12-2011):

+ Added palette commands to disable/enable the plugin in many ways.

+ Added ``codeintel_live_disabled_languages`` and fixed ``codeintel_live`` to disable SublimeCodeIntel live autocomplete mode.

+ Support for new completion settings in Sublime Text 2 Build 2148.

+ JavaScript support improved (it's now much nicer with the CPU).

+ CSS files support much improved (thanks to Jon's new features in autocomplete).

+ Smarter language detection and fallbacks.

+ Improved autocomplete triggering, should now respond better.


License
-------
The plugin is based in code from the Open Komodo Editor and has a MPL license.

Ported from Open Komodo by German M. Bravo (Kronuz).
