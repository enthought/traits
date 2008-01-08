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
from enthought.traits.api import Bool, Enum, implements, Int, Str, Unicode

# Local imports.
from enthought.pyface.i_dialog import IDialog, MDialog
from enthought.pyface.constant import OK, CANCEL, YES, NO
from window import Window


# Map PyQt dialog related constants to the pyface equivalents.
_RESULT_MAP = {
    QtGui.QDialog.Accepted:     OK,
    QtGui.QDialog.Rejected:     CANCEL,
    QtGui.QMessageBox.Ok:       OK,
    QtGui.QMessageBox.Cancel:   CANCEL,
    QtGui.QMessageBox.Yes:      YES,
    QtGui.QMessageBox.No:       NO
}


class Dialog(MDialog, Window):
    """ The toolkit specific implementation of a Dialog.  See the IDialog
    interface for the API documentation.
    """

    implements(IDialog)

    #### 'IDialog' interface ##################################################

    cancel_label = Unicode

    help_id = Str

    help_label = Unicode

    ok_label = Unicode

    resizeable = Bool(True)

    return_code = Int(OK)

    style = Enum('modal', 'nonmodal')

    #### 'IWindow' interface ##################################################

    title = Unicode("Dialog")

    ###########################################################################
    # Protected 'IDialog' interface.
    ###########################################################################

    def _create_buttons(self, parent):
        buttons = QtGui.QDialogButtonBox()

        # 'OK' button.
        # FIXME v3: Review how this is supposed to work for non-modal dialogs
        # (ie. how does anything act on a button click?)
        if self.ok_label:
            btn = buttons.addButton(self.ok_label, QtGui.QDialogButtonBox.AcceptRole)
        else:
            btn = buttons.addButton(QtGui.QDialogButtonBox.Ok)

        btn.setDefault(True)

        # 'Cancel' button.
        # FIXME v3: Review how this is supposed to work for non-modal dialogs
        # (ie. how does anything act on a button click?)
        if self.cancel_label:
            buttons.addButton(self.cancel_label, QtGui.QDialogButtonBox.RejectRole)
        else:
            buttons.addButton(QtGui.QDialogButtonBox.Cancel)

        # 'Help' button.
        # FIXME v3: In the original code the only possible hook into the help
        # was to reimplement self._on_help().  However this was a private
        # method.  Obviously nobody uses the Help button.  For the moment we
        # display it but can't actually use it.
        if len(self.help_id) > 0:
            if self.help_label:
                buttons.addButton(self.help_label, QtGui.QDialogButtonBox.HelpRole)
            else:
                buttons.addButton(QtGui.QDialogButtonBox.Help)

        return buttons

    def _create_contents(self, parent):
        lay = QtGui.QVBoxLayout()

        lay.addWidget(self._create_dialog_area(parent))
        lay.addWidget(self._create_buttons(parent))

        parent.setLayout(lay)

    def _create_dialog_area(self, parent):
        panel = QtGui.QWidget(parent)

        palette = panel.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor('red'))
        panel.setPalette(palette)
        panel.setAutoFillBackground(True)

        return panel

    def _show_modal(self):
        return _RESULT_MAP[self.control.exec_()]

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        dlg = QtGui.QDialog(parent)

        if self.size != (-1, -1):
            dlg.resize(*self.size)

        # FIXME v3: Decide what to do with the resizable trait (ie. set the
        # size policy).
        dlg.setWindowTitle(self.title)

        return dlg

#### EOF ######################################################################
