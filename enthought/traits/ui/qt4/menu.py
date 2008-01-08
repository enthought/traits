#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

"""
Dynamically construct PyQt Menus or MenuBars from a supplied string 
description of the menu.

Menu Description Syntax::
    
    submenu_label {help_string}
        menuitem_label | accelerator {help_string} [~/-name]: code

*submenu_label*
    Label of a sub menu
*menuitem_label*
    Label of a menu item
{*help_string*}    
    Help string to display on the status line (optional)
*accelerator*    
    Accelerator key (e.g., Ctrl-C) (The '|' and keyname are optional, but must
    be used together.)
[~]           
    The menu item is checkable, but is not checked initially (optional)
[/]            
    The menu item is checkable, and is checked initially (optional)
[-]
    The menu item disabled initially (optional)
[*name*]         
    Symbolic name used to refer to menu item (optional)
*code*           
    Python code invoked when menu item is selected
    
A line beginning with a hyphen (-) is interpreted as a menu separator.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re

from PyQt4 import QtGui

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

help_pat    = re.compile( r'(.*){(.*)}(.*)' )
options_pat = re.compile( r'(.*)\[(.*)\](.*)' )

#-------------------------------------------------------------------------------
#  'MakeMenu' class:
#-------------------------------------------------------------------------------

class MakeMenu:
    """ Manages creation of menus.
    """
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, desc, owner, popup = False, window = None ):
        """ Initializes the object.
        """
        self.owner = owner
        if window is None:
            window = owner
        self.window   = window
        self.indirect = getattr( owner, 'call_menu', None )
        self.names    = {}
        self.desc     = desc.split( '\n' )
        self.index    = 0
        if popup:
            self.menu = menu = QtGui.QMenu()
            self.parse( menu, -1 )
        else:
            self.menu = menu = wx.MenuBar()
            self.parse( menu, -1 )
            window.SetMenuBar( menu )

    #---------------------------------------------------------------------------
    #  Recursively parses menu items from the description:
    #---------------------------------------------------------------------------

    def parse ( self, menu, indent ):
        """ Recursively parses menu items from the description.
        """

        while True:

            # Make sure we have not reached the end of the menu description yet:
            if self.index >= len( self.desc ):
                return

            # Get the next menu description line and check its indentation:
            dline    = self.desc[ self.index ]
            line     = dline.lstrip()
            indented = len( dline ) - len( line )
            if indented <= indent:
                return

            # Indicate that the current line has been processed:
            self.index += 1

            # Check for a blank or comment line:
            if (line == '') or (line[0:1] == '#'):
                continue

            # Check for a menu separator:
            if line[0:1] == '-':
                menu.addSeparator()
                continue

            # Extract the help string (if any):
            help  = ''
            match = help_pat.search( line )
            if match:
                help = ' ' + match.group(2).strip()
                line = match.group(1) + match.group(3)

            # Check for a menu item:
            col = line.find( ':' )
            if col >= 0:
                handler = line[ col + 1: ].strip()
                if handler != '':
                    if self.indirect:
                        self.indirect( cur_id, handler )
                        handler = self.indirect
                    else:
                        try:
                            exec ('def handler(event,self=self.owner):\n %s\n' %
                                  handler)
                        except:
                           handler = null_handler
                else:
                    try:
                        exec 'def handler(event,self=self.owner):\n%s\n' % (
                            self.get_body( indented ), ) in globals()
                    except:
                        handler = null_handler

                not_checked = checked = disabled = False
                name = key = ''
                line = line[:col]
                match = options_pat.search(line)
                if match:
                    line = match.group(1) + match.group(3)
                    not_checked, checked, disabled, name = option_check( '~/-',
                             match.group(2).strip() )

                label = line.strip()
                col   = label.find( '|' )
                if col >= 0:
                    key   = label[col + 1:].strip()
                    label = label[:col].strip()

                act = menu.addAction(label, handler)
                act.setCheckable(not_checked or checked)
                act.setStatusTip(help)

                if key:
                    act.setShortcut(key)

                if checked:
                    act.setChecked(True)

                if disabled:
                    act.setEnabled(False)

                if name:
                    self.names[name] = act
                    setattr(self.owner, name, MakeMenuItem(self, act))

            # Else must be the start of a sub menu:
            submenu = QtGui.QMenu(line.strip())

            # Recursively parse the sub-menu:
            self.parse(submenu, indented)

            # Add the menu to its parent:
            act = menu.addMenu(submenu)
            act.setStatusTip(help)

    #---------------------------------------------------------------------------
    #  Returns the body of an inline method:
    #---------------------------------------------------------------------------

    def get_body ( self, indent ):
        """ Returns the body of an inline method.
        """
        result = []
        while self.index < len( self.desc ):
            line = self.desc[ self.index ]
            if (len( line ) - len( line.lstrip() )) <= indent:
                break
            result.append( line )
            self.index += 1
        result = '\n'.join( result ).rstrip()
        if result != '':
            return result
        return '  pass'

    #---------------------------------------------------------------------------
    #  Returns the QAction associated with a specified name:
    #---------------------------------------------------------------------------

    def get_action(self, name):
        """ Returns the QAction associated with a specified name.
        """
        if isinstance(name, basestring):
            return self.names[name]

        return name

    #---------------------------------------------------------------------------
    #  Checks (or unchecks) a menu item specified by name:
    #---------------------------------------------------------------------------

    def checked(self, name, check=None):
        """ Checks (or unchecks) a menu item specified by name.
        """
        act = self.get_action(name)

        if check is None:
            return act.isChecked()

        act.setChecked(check)

    #---------------------------------------------------------------------------
    #  Enables (or disables) a menu item specified by name:
    #---------------------------------------------------------------------------

    def enabled(self, name, enable=None):
        """ Enables (or disables) a menu item specified by name.
        """
        act = self.get_action(name)

        if enable is None:
            return act.isEnabled()

        act.setEnabled(enable)

    #---------------------------------------------------------------------------
    #  Gets/Sets the label for a menu item:
    #---------------------------------------------------------------------------

    def label(self, name, label=None):
        """ Gets or sets the label for a menu item.
        """
        act = self.get_action(name)

        if label is None:
            return unicode(act.text())

        act.setText(label)

#-------------------------------------------------------------------------------
#  'MakeMenuItem' class:
#-------------------------------------------------------------------------------

class MakeMenuItem:
    """ A menu item for a menu managed by MakeMenu.
    """
    def __init__(self, menu, act):
        self.menu = menu
        self.act = act

    def checked(self, check=None):
        return self.menu.checked(self.act, check)

    def toggle(self):
        checked = not self.checked()
        self.checked(checked)
        return checked

    def enabled(self, enable=None):
        return self.menu.enabled(self.act, enable)

    def label(self, label=None):
        return self.menu.label(self.act, label)

#-------------------------------------------------------------------------------
#  Determine whether a string contains any specified option characters, and
#  remove them if it does:
#-------------------------------------------------------------------------------

def option_check ( test, string ):
    """ Determines whether a string contains any specified option characters,
    and removes them if it does.
    """
    result = []
    for char in test:
        col = string.find( char )
        result.append( col >= 0 )
        if col >= 0:
            string = string[ : col ] + string[ col + 1: ]
    return result + [ string.strip() ]

#-------------------------------------------------------------------------------
#  Null menu option selection handler:
#-------------------------------------------------------------------------------

def null_handler ( event ):
    print 'null_handler invoked'
