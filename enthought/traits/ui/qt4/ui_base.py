#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

"""Defines the base class for the PyQt-based Traits UI modal and non-modal
   dialogs.
"""


from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import HasStrictTraits, HasPrivateTraits, Instance, List, Event

from enthought.traits.ui.api \
    import UI

from enthought.traits.ui.menu \
    import Action

from constants \
    import DefaultTitle

from editor \
    import Editor

from helper \
    import restore_window, save_window


#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# List of all predefined system button names:
SystemButtons = ['Undo', 'Redo', 'Apply', 'Revert', 'OK', 'Cancel', 'Help']

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


class BasePanel(object):
    """Base class for Traits UI panels.
    """

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

    def add_button ( self, action, bbox, role, method=None, enabled=True, name=None ):
        """ Creates a button.
        """
        ui = self.ui
        if ((action.defined_when != '') and
            (not ui.eval_when( action.defined_when ))):
            return None

        if name is None:
            name = action.name
        id     = action.id
        button = bbox.addButton(name, role)
        button.setEnabled(enabled)
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

        if method is not None:
            button.connect(button, QtCore.SIGNAL('clicked()'), method)

        if action.tooltip != '':
            button.setToolTip(action.tooltip)

        return button

    def _on_help(self):
        """Handles the user clicking the Help button.
        """
        # FIXME: Needs porting to PyQt.
        self.ui.handler.show_help(self.ui.info, event.GetEventObject())

    def _on_undo(self):
        """Handles a request to undo a change.
        """
        self.ui.history.undo()

    def _on_undoable(self, state):
        """Handles a change to the "undoable" state of the undo history
        """
        self.undo.setEnabled(state)

    def _on_redo(self):
        """Handles a request to redo a change.
        """
        self.ui.history.redo()

    def _on_redoable(self, state):
        """Handles a change to the "redoable" state of the undo history.
        """
        self.redo.setEnabled(state)

    def _on_revert(self):
        """Handles a request to revert all changes.
        """
        ui = self.ui
        ui.history.revert()
        ui.handler.revert(ui.info)

    def _on_revertable(self, state):
        """ Handles a change to the "revert" state.
        """
        self.revert.setEnabled(state)


class BaseDialog(BasePanel):
    """Base class for Traits UI dialog boxes.
    """

    # The different dialog styles.
    NONMODAL, MODAL, POPUP = range(3)

    def init(self, ui, parent, style):
        """Initialise the dialog by creating the controls.
        """
        raise NotImplementedError

    def create_dialog(self, parent, style):
        """Create the dialog control.
        """
        view = self.ui.view

        flags = QtCore.Qt.WindowSystemMenuHint
        if view.resizable:
            flags |= QtCore.Qt.WindowMinMaxButtonsHint
        else:
            flags |= QtCore.Qt.MSWindowsFixedSizeDialogHint

        self.control = control = QtGui.QDialog(parent, flags)

        control.setModal(style == BaseDialog.MODAL)
        control.setWindowTitle(view.title or DefaultTitle)

        QtCore.QObject.connect(control, QtCore.SIGNAL('finished(int)'),
                self._on_finished)

        self._set_icon(view.icon)

    def add_contents(self, panel, buttons):
        """Add a panel (either a widget, layout or None) and optional buttons
           to the dialog.
        """
        # Make sure we have a layout.
        layout = self.control.layout()
        if layout is None:
            layout = QtGui.QVBoxLayout(self.control)

        if not self.ui.view.resizable:
            layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)

        # Add the panel.
        if isinstance(panel, QtGui.QWidget):
            layout.addWidget(panel)
        elif isinstance(panel, QtGui.QLayout):
            layout.addLayout(panel)

        layout.setAlignment(panel, QtCore.Qt.AlignTop)

        # Add the optional buttons.
        if buttons is not None:
            layout.addWidget(buttons)

        # Add the menu bar and tool bar (if any).
        self._add_menubar()
        self._add_toolbar()

    def close(self, rc):
        """Close the dialog and set the given return code.
        """
        save_window(self.ui)
        self.ui.finish(rc)

        self.ui = self.control = None

    @staticmethod
    def display_ui(ui, parent, style):
        """Display the UI.
        """
        ui.owner.init(ui, parent, style)
        ui.control = ui.owner.control
        ui.control._parent = parent

        try:
            ui.prepare_ui()
        except:
            ui.control.setParent(None)
            ui.control.ui = None
            ui.control = None
            ui.owner = None
            ui.result = False
            raise

        ui.handler.position(ui.info)
        restore_window(ui)

        if style == BaseDialog.NONMODAL:
            ui.control.show()
        else:
            ui.control.exec_()

    def _set_icon(self, icon=None):
        """Sets the dialog's icon.
        """
        from enthought.pyface.image_resource import ImageResource

        if not isinstance(icon, ImageResource):
            icon = ImageResource('frame.png')

        self.control.setWindowIcon(icon.create_icon())

    def _on_error(self, errors):
        """Handles editing errors.
        """
        self.ok.setEnable(errors == 0)

    #---------------------------------------------------------------------------
    #  Adds a menu bar to the dialog:
    #---------------------------------------------------------------------------

    def _add_menubar(self):
        """Adds a menu bar to the dialog.
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

    def _add_toolbar ( self ):
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

    def can_add_to_menu(self, action, action_event=None):
        """Returns whether the action should be defined in the user interface.
        """
        if action.defined_when == '':
            return True

        return self.ui.eval_when(action.defined_when)

    def can_add_to_toolbar(self, action):
        """Returns whether the toolbar action should be defined in the user
           interface.
        """
        return self.can_add_to_menu(action)
