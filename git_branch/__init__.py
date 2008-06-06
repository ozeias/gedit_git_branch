# Copyright (C) 2008 - Ozeias Santana(oz.santana@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
from gettext import gettext as _

import gedit
import gtk
import os
import sys
import commands

#Insert menu item
ui_str = """<ui>
  <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_2">
        <menuitem name="Current Git Branch" action="GitBranch"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

class GitBranchPlugin(gedit.Plugin):
    def __init__(self):
        gedit.Plugin.__init__(self)
        self._instances = {}

    def activate(self, window):
        self._instances[window] = GitBranchWindowHelper(self, window)

    def deactivate(self, window):
        self._instances[window].deactivate()
        del self._instances[window]

    def update_ui(self, window):
        self._instances[window].update_ui()

class GitBranchWindowHelper:
    handlers = {}
    
    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin
        self._statusbar = self._window.get_statusbar()
        self._context_id = self._statusbar.get_context_id('GitBranchStatusbar')
        self._status_label = gtk.Label('Git Branch')
        self._frame = gtk.Frame()
     
        self._status_label.set_alignment(0, 0)
        self._status_label.show()
        self._frame.add(self._status_label)
        self._frame.show()
        self._statusbar.add(self._frame)
        self._set_status()
     
        # Insert menu items
        self._insert_menu()

    def deactivate(self):
        # Remove any installed menu items
        self._remove_menu()
     
        self._window = None
        self._plugin = None
        self._action_group = None

    def _insert_menu(self):
        # Get the GtkUIManager
        manager = self._window.get_ui_manager()
     
        # Create a new action group
        self._action_group = gtk.ActionGroup("GitBranchPluginActions")
        self._action_group.add_actions([("GitBranch", None, _("Git Branch"),
                                         '<Control><Alt>b', _("Current Git Branch"),
                                         self.on_git_branch_activate)])
     
        # Insert the action group
        manager.insert_action_group(self._action_group, -1)
     
        # Merge the UI
        self._ui_id = manager.add_ui_from_string(ui_str)

    def _remove_menu(self):
        # Get the GtkUIManager
        manager = self._window.get_ui_manager()
     
        # Remove the ui
        manager.remove_ui(self._ui_id)
     
        # Remove the action group
        manager.remove_action_group(self._action_group)
     
        # Make sure the manager updates
        manager.ensure_update()

    def update_ui(self):
        self._action_group.set_sensitive(self._window.get_active_document() != None)
	if self._window.get_active_document() != None:
		self.on_git_branch_activate("")
    
    def _set_status(self, text=None):
        self._statusbar.pop(self._context_id)
        label = 'Git Branch'
        
        if text is not None:
            label = "Git Branch: %s " % _(text)
        
        self._status_label.set_text(label)
        
    def _get_file_root(self, uri):
        base_dir = os.path.dirname(uri)
        depth = 10
        rails_root = ''

        while depth > 0:
            depth -= 1
            app_dir = os.path.join(base_dir, 'app')
            config_dir = os.path.join(base_dir, 'config')
            if os.path.isdir(app_dir) and os.path.isdir(config_dir):
                rails_root = base_dir
                break
            else:
                base_dir = os.path.abspath(os.path.join(base_dir, '..'))

        return rails_root

    # Menu activate handlers
    def on_git_branch_activate(self, action):
        label=None
        base_dir = os.path.dirname(self._window.get_active_document().get_uri_for_display())
        out=commands.getoutput('cd "' + base_dir + '" && git branch')
        for el in out.split('\n'):
            if  el[0] == '*':
                label = el
            
        if label is not None:
            self._set_status(label)
        else:
            self._set_status('Not a git repository in current directory')
