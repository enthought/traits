#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
# 
# This software is provided without warranty under the terms of the GPL v2
# license.
#------------------------------------------------------------------------------

# Major package imports.
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Bool, Enum, Instance, Tuple

# Local imports.
from enthought.pyface.image_cache import ImageCache
from enthought.pyface.action.action_manager import ActionManager


class ToolBarManager(ActionManager):
    """ A tool bar manager realizes itself in errr, a tool bar control. """

    #### 'ToolBarManager' interface ###########################################

    # The size of tool images (width, height).
    image_size = Tuple((16, 16))

    # The orientation of the toolbar.
    orientation = Enum('horizontal', 'vertical')

    # Should we display the name of each tool bar tool under its image?
    show_tool_names = Bool(True)

    # Should we display the horizontal divider?
    show_divider = Bool(True)

    #### Private interface ####################################################

    # Cache of tool images (scaled to the appropriate size).
    _image_cache = Instance(ImageCache)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, *args, **traits):
        """ Creates a new tool bar manager. """

        # Base class contructor.
        super(ToolBarManager, self).__init__(*args, **traits)

        # An image cache to make sure that we only load each image used in the
        # tool bar exactly once.
        self._image_cache = ImageCache(self.image_size[0], self.image_size[1])

        return

    ###########################################################################
    # 'ToolBarManager' interface.
    ###########################################################################

    def create_tool_bar(self, parent, controller=None):
        """ Creates a tool bar. """

        # If a controller is required it can either be set as a trait on the
        # tool bar manager (the trait is part of the 'ActionManager' API), or
        # passed in here (if one is passed in here it takes precedence over the
        # trait).
        if controller is None:
            controller = self.controller

        # Create the control.
        tool_bar = QtGui.QToolBar(parent)

        tool_bar.setObjectName(self.id)

        if self.show_tool_names:
            tool_bar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        if self.orientation == 'horizontal':
            tool_bar.setOrientation(QtCore.Qt.Horizontal)
        else:
            tool_bar.setOrientation(QtCore.Qt.Vertical)

        # We would normally leave it to the current style to determine the icon
        # size.
        w, h = self.image_size
        tool_bar.setIconSize(QtCore.QSize(w, h))

        # Add all of items in the manager's groups to the tool bar.
        self._qt4_add_tools(parent, tool_bar, controller)

        return tool_bar

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _qt4_add_tools(self, parent, tool_bar, controller):
        """ Adds tools for all items in the list of groups. """

        previous_non_empty_group = None
        for group in self.groups:
            if len(group.items) > 0:
                # Is a separator required?
                if previous_non_empty_group is not None and group.separator:
                    tool_bar.addSeparator()

                previous_non_empty_group = group

                # Create a tool bar tool for each item in the group.
                for item in group.items:
                    item.add_to_toolbar(
                        parent,
                        tool_bar,
                        self._image_cache,
                        controller,
                        self.show_tool_names
                    )

        return

#### EOF ######################################################################
