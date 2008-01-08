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
from enthought.traits.api import Bool, Enum, implements, Instance, Unicode

# Local imports.
from enthought.pyface.i_confirmation_dialog import IConfirmationDialog, MConfirmationDialog
from enthought.pyface.constant import CANCEL, YES, NO
from enthought.pyface.image_resource import ImageResource
from dialog import Dialog


class ConfirmationDialog(MConfirmationDialog, Dialog):
    """ The toolkit specific implementation of a ConfirmationDialog.  See the
    IConfirmationDialog interface for the API documentation.
    """

    implements(IConfirmationDialog)

    #### 'IConfirmationDialog' interface ######################################

    cancel = Bool(False)

    default = Enum(NO, YES, CANCEL)

    image = Instance(ImageResource)

    message = Unicode

    no_label = Unicode

    yes_label = Unicode

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
        dlg = QtGui.QMessageBox(parent)

        dlg.setWindowTitle(self.title)
        dlg.setText(self.message)

        if self.image is None:
            dlg.setIcon(QtGui.QMessageBox.Warning)
        else:
            dlg.setIconPixmap(self.image.create_image())

        # The 'Yes' button.
        if self.yes_label:
            btn = dlg.addButton(self.yes_label, QtGui.QMessageBox.YesRole)
        else:
            btn = dlg.addButton(QtGui.QMessageBox.Yes)

        if self.default == YES:
            dlg.setDefaultButton(btn)

        # The 'No' button.
        if self.no_label:
            btn = dlg.addButton(self.no_label, QtGui.QMessageBox.NoRole)
        else:
            btn = dlg.addButton(QtGui.QMessageBox.No)

        if self.default == NO:
            dlg.setDefaultButton(btn)

        # The 'Cancel' button.
        if self.cancel:
            if self.cancel_label:
                btn = dlg.addButton(self.cancel_label, QtGui.QMessageBox.RejectRole)
            else:
                btn = dlg.addButton(QtGui.QMessageBox.Cancel)

            if self.default == CANCEL:
                dlg.setDefaultButton(btn)

        return dlg

#### EOF ######################################################################
