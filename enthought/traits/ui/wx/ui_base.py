#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: David C. Morrill
# Date: 12/18/2004
#------------------------------------------------------------------------------
""" Defines the base class for the wxPython-based Traits UI modal and non-modal
dialogs.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import HasStrictTraits, HasPrivateTraits, Instance, List, Event

from enthought.traits.ui.api \
    import UI

from enthought.traits.ui.menu \
    import Action

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# List of all predefined system button names:
SystemButtons = [ 'Undo', 'Redo', 'Apply', 'Revert', 'OK', 'Cancel', 'Help' ]

#-------------------------------------------------------------------------------
#  'RadioGroup' class:
#-------------------------------------------------------------------------------

class RadioGroup ( HasStrictTraits ):
    """ A group of mutually-exclusive menu or toolbar actions.
    """
    # List of menu or tool bar items
    items = List  

    #---------------------------------------------------------------------------
    #  Handles a menu item in the group being checked:
    #---------------------------------------------------------------------------

    def menu_checked ( self, menu_item ):
        """ Handles a menu item in the group being checked.
        """
        for item in self.items:
            if item is not menu_item:
                item.control.Check( False )
                item.item.action.checked = False

    #---------------------------------------------------------------------------
    #  Handles a tool bar item in the group being checked:
    #---------------------------------------------------------------------------

    def toolbar_checked ( self, toolbar_item ):
        """ Handles a tool bar item in the group being checked.
        """
        for item in self.items:
            if item is not toolbar_item:
                item.tool_bar.ToggleTool( item.control_id, False )
                item.item.action.checked = False

#-------------------------------------------------------------------------------
#  'ButtonEditor' class:
#-------------------------------------------------------------------------------

class ButtonEditor ( Editor ):
    """ Editor for buttons.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Action associated with the button
    action = Instance( Action )

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, **traits ):
        self.set( **traits )

    #---------------------------------------------------------------------------
    #  Handles the associated button being clicked:
    #---------------------------------------------------------------------------

    def perform ( self, event ):
        """ Handles the associated button being clicked.
        """
        self.ui.do_undoable( self._perform, event )

    def _perform ( self, event ):
        method_name = self.action.action
        if method_name == '':
            method_name = '_%s_clicked' % (self.action.name.lower())
        method = getattr( self.ui.handler, method_name, None )
        if method is not None:
            method( self.ui.info )
        else:
            self.action.perform( event )

#-------------------------------------------------------------------------------
#  'BaseDialog' class:
#-------------------------------------------------------------------------------

class BaseDialog ( object ):
    """ Base class for Traits UI dialog boxes.
    """
    #---------------------------------------------------------------------------
    #  Sets the frame's icon:
    #---------------------------------------------------------------------------

    def set_icon ( self, icon = None ):
        """ Sets the frame's icon.
        """
        from enthought.pyface.image_resource import ImageResource

        if not isinstance( icon, ImageResource ):
            icon = ImageResource( 'frame.ico' )
        self.control.SetIcon( icon.create_icon() )

    #---------------------------------------------------------------------------
    #  Adds a menu bar to the dialog:
    #---------------------------------------------------------------------------

    def add_menubar ( self ):
        """ Adds a menu bar to the dialog.
        """
        menubar = self.ui.view.menubar
        if menubar is not None:
            self._last_group = self._last_parent = None
            self.control.SetMenuBar(
                menubar.create_menu_bar( self.control, self ) )
            self._last_group = self._last_parent = None

    #---------------------------------------------------------------------------
    #  Adds a tool bar to the dialog:
    #---------------------------------------------------------------------------

    def add_toolbar ( self ):
        """ Adds a toolbar to the dialog.
        """
        toolbar = self.ui.view.toolbar
        if toolbar is not None:
            self._last_group = self._last_parent = None
            self.control.SetToolBar(
                toolbar.create_tool_bar( self.control, self ) )
            self._last_group = self._last_parent = None

    #---------------------------------------------------------------------------
    #  Adds a menu item to the menu bar being constructed:
    #---------------------------------------------------------------------------

    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        item   = menu_item.item
        action = item.action

        if action.id != '':
            self.ui.info.bind( action.id, menu_item )

        if action.style == 'radio':
            if ((self._last_group is None) or
                (self._last_parent is not item.parent)):
                self._last_group = RadioGroup()
                self._last_parent = item.parent
            self._last_group.items.append( menu_item )
            menu_item.group = self._last_group

        if action.enabled_when != '':
            self.ui.add_enabled( action.enabled_when, menu_item )

        if action.checked_when != '':
            self.ui.add_checked( action.checked_when, menu_item )

    #---------------------------------------------------------------------------
    #  Adds a tool bar item to the tool bar being constructed:
    #---------------------------------------------------------------------------

    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a toolbar item to the toolbar being constructed.
        """
        self.add_to_menu( toolbar_item )

    #---------------------------------------------------------------------------
    #  Returns whether the menu action should be defined in the user interface:
    #---------------------------------------------------------------------------

    def can_add_to_menu ( self, action ):
        """ Returns whether the action should be defined in the user interface.
        """
        if action.defined_when == '':
            return True

        return self.ui.eval_when( action.defined_when )

    #---------------------------------------------------------------------------
    #  Returns whether the toolbar action should be defined in the user
    #  interface:
    #---------------------------------------------------------------------------

    def can_add_to_toolbar ( self, action ):
        """ Returns whether the toolbar action should be defined in the user
            interface.
        """
        return self.can_add_to_menu( action )

    #---------------------------------------------------------------------------
    #  Performs the action described by a specified Action object:
    #---------------------------------------------------------------------------

    def perform ( self, action ):
        """ Performs the action described by a specified Action object.
        """
        self.ui.do_undoable( self._perform, action )

    def _perform ( self, action ):
        method = getattr( self.ui.handler, action.action, None )
        if method is not None:
            method( self.ui.info )
        else:
            action.perform()

    #---------------------------------------------------------------------------
    #  Check to see if a specified 'system' button is in the buttons list, and
    # add it if it is not:
    #---------------------------------------------------------------------------

    def check_button ( self, buttons, action ):
        """ Adds *action* to the system buttons list for this dialog, if it is
        not already in the list.
        """
        name = action.name
        for button in buttons:
            if self.is_button( button, name ):
                return
        buttons.append( action )

    #---------------------------------------------------------------------------
    #  Check to see if a specified Action button is a 'system' button:
    #---------------------------------------------------------------------------

    def is_button ( self, action, name ):
        """ Returns whether a specified action button is a system button.
        """
        if isinstance(action, basestring):
            return (action == name)
        return (action.name == name)

    #---------------------------------------------------------------------------
    #  Coerces a string to an Action if necessary:
    #---------------------------------------------------------------------------

    def coerce_button ( self, action ):
        """ Coerces a string to an Action if necessary.
        """
        if isinstance(action, basestring):
            return Action( name   = action,
                           action = '?'[ (not action in SystemButtons): ] )
        return action

    #---------------------------------------------------------------------------
    #  Creates a user specified button:
    #---------------------------------------------------------------------------

    def add_button ( self, action, sizer, method  = None,
                                          enabled = True,
                                          name    = None ):
        """ Creates a button.
        """
        ui = self.ui
        if ((action.defined_when != '') and
            (not ui.eval_when( action.defined_when ))):
            return None

        if name is None:
            name = action.name
        id     = action.id
        button = wx.Button( self.control, -1, name )
        button.Enable( enabled )
        if (method is None) or (action.enabled_when != '') or (id != ''):
            editor = ButtonEditor( ui      = ui,
                                   action  = action,
                                   control = button )
            if id != '':
                ui.info.bind( id, editor )
            if action.visible_when != '':
                ui.add_visible( action.visible_when, editor )
            if action.enabled_when != '':
                ui.add_enabled( action.enabled_when, editor )
            if method is None:
                method = editor.perform
        wx.EVT_BUTTON( self.control, button.GetId(), method )
        sizer.Add( button, 0, wx.LEFT, 5 )
        if action.tooltip != '':
            button.SetToolTipString( action.tooltip )
        return button

