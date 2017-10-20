from __future__ import absolute_import, unicode_literals, print_function

import os
import json
from copy import deepcopy
from collections import defaultdict

import sublime
import sublime_plugin


class Settings(object):
    """This class provides global access to and management of plugin settings."""

    def __init__(self, name):
        """Initialize a new instance."""
        self.name = name
        self.settings = {}
        self.previous_settings = {}
        self.changeset = set()
        self.plugin_settings = None
        self.edits = defaultdict(list)

    def load(self, force=False):
        """Load the plugin settings."""
        if force or not self.settings:
            self.observe()
            self.on_change()

    def has_setting(self, setting):
        """Return whether the given setting exists."""
        return setting in self.settings

    def get(self, setting, default=None):
        """Return a plugin setting, defaulting to default if not found."""
        return self.settings.get(setting, default)

    def set(self, setting, value, changed=False):
        """
        Set a plugin setting to the given value.

        Clients of this module should always call this method to set a value
        instead of doing settings['foo'] = 'bar'.

        If the caller knows for certain that the value has changed,
        they should pass changed=True.

        """
        self.copy()
        self.settings[setting] = value

        if changed:
            self.changeset.add(setting)

    def pop(self, setting, default=None):
        """
        Remove a given setting and return default if it is not in self.settings.

        Clients of this module should always call this method to pop a value
        instead of doing settings.pop('foo').

        """
        self.copy()
        return self.settings.pop(setting, default)

    def copy(self):
        """Save a copy of the plugin settings."""
        self.previous_settings = deepcopy(self.settings)

    def observe(self, observer=None):
        """Observer changes to the plugin settings."""
        self.plugin_settings = sublime.load_settings('{}.sublime-settings'.format(self.name))
        self.plugin_settings.clear_on_change(self.name)
        self.plugin_settings.add_on_change(self.name, observer or self.on_change)

    def merge_user_settings(self, settings):
        """
        Return the default settings merged with the user's settings.
        If there are any nested settings, those get merged as well.

        """

        default = settings.get('default', {})
        user = settings.get('user', {})

        if user:
            for setting_name in self.nested_settings:
                default_setting = default.pop(setting_name, {})
                user_setting = user.get(setting_name, {})

                for name, data in user_setting.items():
                    if name in default_setting and isinstance(default_setting[name], dict):
                        default_setting[name].update(data)
                    else:
                        default_setting[name] = data
                default[setting_name] = default_setting
                user.pop(setting_name, None)
            default.update(user)

        return default

    def on_change(self):
        """Update state when the user settings change."""

        settings = self.merge_user_settings(self.plugin_settings)
        self.settings.clear()
        self.settings.update(settings)

        self.on_update()

        self.changeset.clear()
        self.copy()

    def on_update(self):
        """To be implemented by the user, when needed."""
        pass

    def save(self, view=None):
        """
        Regenerate and save the user settings.

        User settings are updated and merged with the default settings and if
        the user settings are currently being edited, the view is also updated.

        """
        self.load()

        # Fill in default settings
        settings = self.settings

        settings_filename = '{}.sublime-settings'.format(self.name)
        user_settings_path = os.path.join(sublime.packages_path(), 'User', settings_filename)
        settings_views = []

        if view is None:
            # See if any open views are the user prefs
            for window in sublime.windows():
                for view in window.views():
                    if view.file_name() == user_settings_path:
                        settings_views.append(view)
        else:
            settings_views = [view]

        if settings_views:
            def replace(edit):
                if not view.is_dirty():
                    j = json.dumps({'user': settings}, indent=4, sort_keys=True)
                    j = j.replace(' \n', '\n')
                    view.replace(edit, sublime.Region(0, view.size()), j)

            for view in settings_views:
                self.edits[view.id()].append(replace)
                view.run_command('settings_view_editor', self)
                view.run_command('save')
        else:
            user_settings = sublime.load_settings(settings_filename)
            user_settings.set('user', settings)
            sublime.save_settings(settings_filename)

    def edit(self, vid, edit):
        """Perform an operation on a view with the given edit object."""
        callbacks = self.edits.pop(vid, [])

        for c in callbacks:
            c(edit)


class SettingsViewEditorCommand(sublime_plugin.TextCommand):
    """A plugin command used to generate an edit object for a view."""

    def run(self, edit, settings):
        """Run the command."""
        settings.edit(self.view.id(), edit)
