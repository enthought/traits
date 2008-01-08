#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------
""" The PyQt specific implementation of a menu manager. """


# Major package imports.
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Unicode

# Local imports.
from enthought.pyface.action.action_manager import ActionManager
from enthought.pyface.action.action_manager_item import ActionManagerItem
from enthought.pyface.action.group import Group


class MenuManager(ActionManager, ActionManagerItem):
    """ A menu manager realizes itself in a menu control.

    This could be a sub-menu or a context (popup) menu.
    """

    #### 'MenuManager' interface ##############################################
    
    # The menu manager's name (if the manager is a sub-menu, this is what its
    # label will be).
    name = Unicode

    ###########################################################################
    # 'MenuManager' interface.
    ###########################################################################

    def create_menu(self, parent, controller=None):
        """ Creates a menu representation of the manager. """

        # If a controller is required it can either be set as a trait on the
        # menu manager (the trait is part of the 'ActionManager' API), or
        # passed in here (if one is passed in here it takes precedence over the
        # trait).
        if controller is None:
            controller = self.controller

        return _Menu(self, parent, controller)

    ###########################################################################
    # 'ActionManagerItem' interface.
    ###########################################################################

    def add_to_menu(self, parent, menu, controller):
        """ Adds the item to a menu. """

        submenu = self.create_menu(parent, controller)
        submenu.menuAction().setText(self.name)
        menu.addMenu(submenu)

    def add_to_toolbar(self, parent, tool_bar, image_cache, controller):
        """ Adds the item to a tool bar. """

        raise ValueError("Cannot add a menu manager to a toolbar.")


class _Menu(QtGui.QMenu):
    """ The toolkit-specific menu control. """

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, manager, parent, controller):
        """ Creates a new tree. """

        # Base class constructor.
        QtGui.QMenu.__init__(self, parent)

        # The parent of the menu.
        self._parent = parent

        # The manager that the menu is a view of.
        self._manager = manager

        # The controller.
        self._controller = controller

        # Create the menu structure.
        self.refresh()

        # Listen to the manager being updated.
        self._manager.on_trait_change(self.refresh, 'changed')

    ###########################################################################
    # '_Menu' interface.
    ###########################################################################

    def is_empty(self):
        """ Is the menu empty? """

        return self.isEmpty()

    def refresh(self):
        """ Ensures that the menu reflects the state of the manager. """

        self.clear()

        manager = self._manager
        parent  = self._parent

        previous_non_empty_group = None

        for group in manager.groups:
            previous_non_empty_group = self._add_group(parent, group,
                    previous_non_empty_group)

    def show(self, x, y):
        """ Show the menu at the specified location. """

        self.popup(QtCore.QPoint(x, y))

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _add_group(self, parent, group, previous_non_empty_group=None):
        """ Adds a group to a menu. """

        if len(group.items) > 0:
            # Is a separator required?
            if previous_non_empty_group is not None and group.separator:
                self.addSeparator()

            # Create actions and sub-menus for each contribution item in
            # the group.
            for item in group.items:
                if isinstance(item, Group):
                    if len(item.items) > 0:
                        self._add_group(parent, item, previous_non_empty_group)

                        if previous_non_empty_group is not None \
                           and previous_non_empty_group.separator \
                           and item.separator:
                            self.addSeparator()

                        previous_non_empty_group = item

                else:
                    item.add_to_menu(parent, self, self._controller)

            previous_non_empty_group = group

        return previous_non_empty_group

#### EOF ######################################################################
