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
from enthought.traits.api import Enum, implements, Unicode

# Local imports.
from enthought.pyface.i_message_dialog import IMessageDialog, MMessageDialog
from dialog import Dialog


# Map the ETS severity to the corresponding PyQt standard icon.
_SEVERITY_TO_ICON_MAP = {
    'information':  QtGui.QMessageBox.Information,
    'warning':      QtGui.QMessageBox.Warning,
    'error':        QtGui.QMessageBox.Critical
}


class MessageDialog(MMessageDialog, Dialog):
    """ The toolkit specific implementation of a MessageDialog.  See the
    IMessageDialog interface for the API documentation.
    """

    implements(IMessageDialog)

    #### 'IMessageDialog' interface ###########################################

    message = Unicode

    severity = Enum('information', 'warning', 'error')

    ###########################################################################
    # Protected 'IDialog' interface.
    ###########################################################################

    def _create_contents(self, parent):
        # In PyQt this is a canned dialog.
        pass

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        return QtGui.QMessageBox(_SEVERITY_TO_ICON_MAP[self.severity],
                self.title, self.message, QtGui.QMessageBox.Ok, parent)

#### EOF ######################################################################
