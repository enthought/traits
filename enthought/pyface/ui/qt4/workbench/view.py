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


# Enthought library imports.
from enthought.pyface.workbench.i_view import MView


class View(MView):
    """ The toolkit specific implementation of a View.

    See the IView interface for the API documentation.
    
    """

    ###########################################################################
    # 'IWorkbenchPart' interface.
    ###########################################################################

    def create_control(self, parent):
        """ Create the toolkit-specific control that represents the part. """

        from PyQt4 import QtGui

        control = QtGui.QWidget(parent)

        palette = control.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor('red'))
        control.setPalette(palette)
        control.setAutoFillBackground(True)

        return control

    def destroy_control(self):
        """ Destroy the toolkit-specific control that represents the part. """

        if self.control is not None:
            self.control.setParent(None)
            self.control = None

        return

    def set_focus(self):
        """ Set the focus to the appropriate control in the part. """

        if self.control is not None:
            self.control.setFocus()

        return
    
#### EOF ######################################################################
