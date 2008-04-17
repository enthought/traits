#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

"""Creates a PyQt user interface for a specified UI object, where the UI is
   "live", meaning that it immediately updates its underlying object(s).
"""


from PyQt4 import QtCore, QtGui

from enthought.traits.ui.undo \
    import UndoHistory

from enthought.traits.ui.menu \
    import UndoButton, RevertButton, OKButton, CancelButton, HelpButton

from ui_base \
    import BaseDialog

from ui_panel \
    import panel


#-------------------------------------------------------------------------------
#  Create the different 'live update' PyQt user interfaces.
#-------------------------------------------------------------------------------

def ui_live(ui, parent):
    """Creates a live, non-modal PyQt user interface for a specified UI object.
    """
    _ui_dialog(ui, parent, BaseDialog.NONMODAL)

def ui_livemodal(ui, parent):
    """Creates a live, modal PyQt user interface for a specified UI object.
    """
    _ui_dialog(ui, parent, BaseDialog.MODAL)

def ui_popup(ui, parent):
    """Creates a live, modal popup PyQt user interface for a specified UI
       object.
    """
    _ui_dialog(ui, parent, BaseDialog.POPUP)


def _ui_dialog(ui, parent, style):
    """Creates a live PyQt user interface for a specified UI object.
    """
    if ui.owner is None:
        ui.owner = _LiveWindow()

    BaseDialog.display_ui(ui, parent, style)


class _LiveWindow(BaseDialog):
    """User interface window that immediately updates its underlying object(s).
    """

    def init(self, ui, parent, style):
        """Initialise the object.

           FIXME: Note that we treat MODAL and POPUP as equivalent until we
           have an example that demonstrates how POPUP is supposed to work.
        """
        self.ui = ui
        self.control = ui.control
        view = ui.view
        history = ui.history

        if self.control is not None:
            if history is not None:
                history.on_trait_change(self._on_undoable, 'undoable',
                        remove=True)
                history.on_trait_change(self._on_redoable, 'redoable',
                        remove=True)
                history.on_trait_change(self._on_revertable, 'undoable',
                        remove=True)

            ui.reset()
        else:
            self.create_dialog(parent, style)

        self.set_icon(view.icon)

        # Convert the buttons to actions.
        buttons = [self.coerce_button(button) for button in view.buttons]
        nr_buttons = len(buttons)

        no_buttons = ((nr_buttons == 1) and self.is_button(buttons[0], ''))

        has_buttons = ((not no_buttons) and ((nr_buttons > 0) or view.undo or
                view.revert or view.ok or view.cancel))

        if has_buttons or (view.menubar is not None):
            if history is None:
                history = UndoHistory()
        else:
            history = None

        ui.history = history

        if (not no_buttons) and (has_buttons or view.help):
            bbox = QtGui.QDialogButtonBox()

            # Create the necessary special function buttons.
            if nr_buttons == 0:
                if view.undo:
                    self.check_button(buttons, UndoButton)
                if view.revert:
                    self.check_button(buttons, RevertButton)
                if view.ok:
                    self.check_button(buttons, OKButton)
                if view.cancel:
                    self.check_button(buttons, CancelButton)
                if view.help:
                    self.check_button(buttons, HelpButton)

            for button in buttons:
                if self.is_button(button, 'Undo'):
                    self.undo = self.add_button(button, bbox,
                            QtGui.QDialogButtonBox.ActionRole, self._on_undo,
                            False)
                    history.on_trait_change(self._on_undoable, 'undoable',
                            dispatch='ui')
                    if history.can_undo:
                        self._on_undoable(True)

                    self.redo = self.add_button(button, bbox, 
                            QtGui.QDialogButtonBox.ActionRole, self._on_redo,
                            False, 'Redo')
                    history.on_trait_change(self._on_redoable, 'redoable',
                            dispatch='ui')
                    if history.can_redo:
                        self._on_redoable(True)

                elif self.is_button(button, 'Revert'): 
                    self.revert = self.add_button(button, bbox,
                            QtGui.QDialogButtonBox.ResetRole, self._on_revert,
                            False)
                    history.on_trait_change(self._on_revertable, 'undoable',
                            dispatch='ui')
                    if history.can_undo:
                        self._on_revertable(True)

                elif self.is_button(button, 'OK'): 
                    self.ok = self.add_button(button, bbox,
                            QtGui.QDialogButtonBox.AcceptRole,
                            self.control.accept)
                    ui.on_trait_change(self._on_error, 'errors', dispatch='ui')

                elif self.is_button(button, 'Cancel'): 
                    self.add_button(button, bbox,
                            QtGui.QDialogButtonBox.RejectRole,
                            self.control.reject)

                elif self.is_button(button, 'Help'): 
                    self.add_button(button, bbox,
                            QtGui.QDialogButtonBox.HelpRole, self._on_help)

                elif not self.is_button(button, ''):
                    self.add_button(button, bbox,
                            QtGui.QDialogButtonBox.ActionRole)

        else:
            bbox = None

        self.add_contents(panel(ui), bbox)

    def close(self, rc):            
        """Close the dialog and set the given return code.
        """
        super(_LiveWindow, self).close(rc)

        self.undo = self.redo = self.revert = None

    def _on_finished(self, result):
        """Handles the user finishing with the dialog.
        """
        accept = bool(result)

        if not accept and self.ui.history is not None:
            self._on_revert()

        self.close(accept)
