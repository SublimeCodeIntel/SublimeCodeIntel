Sublime CodeIntel
=================

Code intelligence plugin ported from Open Komodo Editor to the [Sublime Text 2](http://sublimetext.com "Sublime Text 2") editor.

Supports all the languages Komodo Editor supports for Code Intelligence (CIX, CodeIntel2):

Provides the following features:

* Jump to Symbol Definition - Jump to the file and line of the definition of a symbol.
* Imports autocomplete - Shows autocomplet with the available modules/symbols in real time.
* Function Call tooltips - Displays information in the status bar about the working function.

Currently it only works on MacOS X. Two libraries need to be compiled for it to work in other platforms: `SilverCity` and `ciElements`

Installing
-----

*Without Git:* Download the latest source from http://github.com/Kronuz/SublimeCodeIntel and copy the whole directory into the Packages directory.

*With Git:* Clone the repository in your Sublime Text Packages directory (located one folder above the "User" directory)

> git clone git://github.com/Kronuz/SublimeCodeIntel.git


The "User" packages directory is located at:

* Windows:
    %APPDATA%/Sublime Text 2/Packages/
* OS X:
    ~/Library/Application Support/Sublime Text 2/Packages/
* Linux:
    ~/.Sublime Text 2/Packages/

Don't forget to add key or mouse bindings. For "Jump to Symbol Declaration":
    Setup in User Key Bindings:
        `{ "keys": ["super+f3"], "command": "goto_python_definition" }`
    ...or in User Mouse Bindings (super + click):
        `{ "button": "button1", "modifiers": ["super"], "command": "goto_python_definition" }`

Configuration files (`~/.codeintel/config' or `project_root/.codeintel/config'). Example::

    {
        "PHP": {
            "php": '/usr/bin/php',
            "phpExtraPaths": [],
            "phpConfigFile": 'php.ini',
        },
        "JavaScript": {
            "javascriptExtraPaths": [],
        },
        "Perl": {
            "perl": "/usr/bin/perl",
            "perlExtraPaths": [],
        },
        "Perl": {
            "ruby": "/usr/bin/ruby",
            "rubyExtraPaths": [],
        },
        "Python": {
            "python": '/usr/bin/python',
            "pythonExtraPaths": [],
        },
        "Python3": {
            "python": '/usr/bin/python3',
            "pythonExtraPaths": [],
        },
    }

Using
-----
Start typing, use the `goto_python_definition` with the key or mouse bindings.

Don't despair! The first time you use it it needs to build some indexes and it can take more than a few seconds (around six in my configuration).

It just works!
