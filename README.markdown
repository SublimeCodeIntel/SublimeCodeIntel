Sublime CodeIntel
=================

Code intelligence plugin ported from Open Komodo Editor to the [Sublime Text 2](http://sublimetext.com "Sublime Text 2") editor.

Supports all the languages Komodo Editor supports for Code Intelligence (CIX, CodeIntel2):
    PHP, Python, RHTML, JavaScript, Smarty, Mason, Node.js, XBL, Tcl, HTML, HTML5, TemplateToolkit, XUL, Django, Perl, Ruby, Python3.

Provides the following features:

* Jump to Symbol Definition - Jump to the file and line of the definition of a symbol.
* Imports autocomplete - Shows autocomplete with the available modules/symbols in real time.
* Function Call tooltips - Displays information in the status bar about the working function.

Plugin should work in all three platforms (MacOS X, Windows and Linux).


Installing
----------
*Without Git:* Download the latest source from http://github.com/Kronuz/SublimeCodeIntel and copy the whole directory into the Packages directory.

*With Git:* Clone the repository in your Sublime Text 2 Packages directory, located somewhere in user's "Home" directory:

> git clone git://github.com/Kronuz/SublimeCodeIntel.git


The "Packages" packages directory is located at:

* Windows:
    %APPDATA%/Sublime Text 2/Packages/
* OS X:
    ~/Library/Application Support/Sublime Text 2/Packages/
* Linux:
    ~/.Sublime Text 2/Packages/


Using
-----

* Sublime CodeIntel will allow you to jump around symbol definitions even across files with just a click. To "Jump to Symbol Declaration" use `super+f3` or `alt+click` over the symbol.

* Start typing code as usual, autocomplete will pop up whenever it's available. To trigger manual codeintel autocompletion use `super+j`.

Don't despair! The first time you use it it needs to build some indexes and it can take more than a few seconds (around six in my configuration).

It just works!


Configuring
-----------
For adding additional library paths (django and extra libs paths for Python or extra paths to look for .js files for JavaScript for example), either add those paths as folders to your project, or create an optional codeintel configuration file in your home or in your project's root.

Configuration files (`~/.codeintel/config` or `project_root/.codeintel/config`). All configurations are optional. Example::

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
        "Perl": {
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

* Live autocomplete can be disabled by setting "codeintel_live" to false.

* A list of disabled languages can be set using "codeintel_disabled_languages". Ex. ``"codeintel_disabled_languages": ['css']`


License
-------
The plugin is based in code from the Open Komodo Editor and has a MPL license.

Ported from Open Komodo by German M. Bravo (Kronuz).
