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


# Major package imports.
from PyQt4 import QtGui

# Enthought library imports.
from enthought.pyface.action.api import MenuBarManager, StatusBarManager
from enthought.pyface.action.api import ToolBarManager
from enthought.traits.api import implements, Instance, Unicode

# Local imports.
from enthought.pyface.i_application_window import IApplicationWindow, MApplicationWindow
from enthought.pyface.image_resource import ImageResource
from window import Window


class ApplicationWindow(MApplicationWindow, Window):
    """ The toolkit specific implementation of an ApplicationWindow.  See the
    IApplicationWindow interface for the API documentation.
    """

    implements(IApplicationWindow)

    #### 'IApplicationWindow' interface #######################################

    icon = Instance(ImageResource)

    menu_bar_manager = Instance(MenuBarManager)

    status_bar_manager = Instance(StatusBarManager)

    tool_bar_manager = Instance(ToolBarManager)

    #### 'IWindow' interface ##################################################

    title = Unicode("Pyface")

    ###########################################################################
    # Protected 'IApplicationWindow' interface.
    ###########################################################################

    def _create_contents(self, parent):
        panel = QtGui.QWidget(parent)

        palette = panel.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor('blue'))
        panel.setPalette(palette)
        panel.setAutoFillBackground(True)

        return panel

    def _create_menu_bar(self, parent):
        if self.menu_bar_manager is not None:
            menu_bar = self.menu_bar_manager.create_menu_bar(parent)
            self.control.setMenuBar(menu_bar)

    def _create_status_bar(self, parent):
        if self.status_bar_manager is not None:
            status_bar = self.status_bar_manager.create_status_bar(parent)
            self.control.setStatusBar(status_bar)

    def _create_tool_bar(self, parent):
        if self.tool_bar_manager is not None:
            tool_bar = self.tool_bar_manager.create_tool_bar(parent)
            self.control.addToolBar(tool_bar)

            # Make sure that the tool bar has a name so that its state can be
            # saved.
            if tool_bar.objectName().isEmpty():
                tool_bar.setObjectName('__toolbar__')

    def _set_window_icon(self):
        if self.icon is None:
            icon = ImageResource('application.png')
        else:
            icon = self.icon

        self.control.setWindowIcon(icon.create_icon())

    ###########################################################################
    # 'Window' interface.
    ###########################################################################

    def _size_default(self):
        """ Trait initialiser. """

        return (800, 600)

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create(self):
        super(ApplicationWindow, self)._create()

        contents = self._create_contents(self.control)
        self.control.setCentralWidget(contents)

        self._create_trim_widgets(self.control)

    def _create_control(self, parent):
        control = QtGui.QMainWindow(parent)

        if self.position != (-1, -1):
            control.move(*self.position)

        if self.size != (-1, -1):
            control.resize(*self.size)

        control.setWindowTitle(self.title)
        control.setDockNestingEnabled(True)
        control.setAnimated(False)

        return control

#### EOF ######################################################################
