#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

"""Creates a PyQt user interface for a specified UI object.
"""


from PyQt4 import QtCore, QtGui

from enthought.traits.ui.menu \
    import ApplyButton, RevertButton, OKButton, CancelButton, HelpButton

from ui_base \
    import BaseDialog

from ui_panel \
    import panel


#-------------------------------------------------------------------------------
#  Create the different modal PyQt user interfaces.
#-------------------------------------------------------------------------------

def ui_modal(ui, parent):
    """Creates a modal PyQt user interface for a specified UI object.
    """
    _ui_dialog(ui, parent, BaseDialog.MODAL)

def ui_nonmodal(ui, parent):
    """Creates a non-modal PyQt user interface for a specified UI object.
    """
    _ui_dialog(ui, parent, BaseDialog.NONMODAL)


def _ui_dialog(ui, parent, style):
    """Creates a PyQt dialog box for a specified UI object.

       Changes are not immediately applied to the underlying object.  The user
       must click **Apply** or **OK** to apply changes.  The user can revert
       changes by clicking **Revert** or **Cancel**.
    """
    if ui.owner is None:
        ui.owner = _ModalDialog()

    BaseDialog.display_ui(ui, parent, style)


class _ModalDialog(BaseDialog):
    """Modal dialog box for Traits-based user interfaces.
    """

    def init(self, ui, parent, style):
        """Initialise the object.
        """
        self.ui = ui
        self.control = ui.control
        view = ui.view

        revert = apply = False

        if self.control is not None:
            if hasattr(self, 'revert'):
                revert = self.revert.isEnabled()

            if hasattr(self, 'apply'):
                apply = self.apply.isEnabled()

            ui.reset()
        else:
            self.create_dialog(parent, style)

            # Create the 'context' copies we will need while editing:
            context = ui.context
            ui._context = context
            ui.context = self._copy_context(context)
            ui._revert = self._copy_context(context)

        # Convert the buttons to actions.
        buttons = [self.coerce_button(button) for button in view.buttons]
        nr_buttons = len(buttons)

        if (nr_buttons != 1) or (not self.is_button(buttons[0], '')):
            bbox = QtGui.QDialogButtonBox()

            # Create the necessary special function buttons.
            if nr_buttons == 0:
                if view.apply:
                    self.check_button(buttons, ApplyButton)
                    if view.revert:
                        self.check_button(buttons, RevertButton)
                if view.ok:
                    self.check_button(buttons, OKButton)
                if view.cancel:
                    self.check_button(buttons, CancelButton)
                if view.help:
                    self.check_button(buttons, HelpButton)

            for button in buttons:
                if self.is_button(button, 'Apply'):
                    self.apply = self.add_button(button, bbox,
                            QtGui.QDialogButtonBox.ApplyRole, self._on_apply,
                            apply)
                    ui.on_trait_change(self._on_applyable, 'modified',
                            dispatch='ui')

                elif self.is_button(button, 'Revert'):
                    self.revert = self.add_button(button, bbox, 
                            QtGui.QDialogButtonBox.ResetRole, self._on_revert,
                            revert)

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
        super(_ModalDialog, self).close(rc)

        self.apply = self.revert = self.help = None

    def _copy_context(self, context):
        """Creates a copy of a *context* dictionary.
        """
        result = {}
        for name, value in context.items():
            if value is not None:
                result[name] = value.clone_traits()
            else:
                result[name] = None

        return result

    def _apply_context(self, from_context, to_context):
        """Applies the traits in the *from_context* to the *to_context*.
        """
        for name, value in from_context.items():
            if value is not None:
                to_context[name].copy_traits(value)
            else:
                to_context[name] = None

        if to_context is self.ui._context:
            on_apply = self.ui.view.on_apply
            if on_apply is not None:
                on_apply()

    def _on_finished(self, result):
        """Handles the user finishing with the dialog.
        """
        accept = bool(result)

        if accept:
            self._apply_context(self.ui.context, self.ui._context)
        else:
            self._apply_context(self.ui._revert, self.ui._context)

        self.close(accept)

    def _on_apply(self):
        """Handles a request to apply changes.
        """
        ui = self.ui
        self._apply_context(ui.context, ui._context)
        self.revert.setEnabled(True)
        ui.handler.apply(ui.info)
        ui.modified = False

    def _on_applyable(self, state):
        """Handles a change to the "modified" state of the user interface .
        """
        self.apply.setEnabled( state )

    def _on_revert(self):
        """Handles a request to revert changes.
        """
        ui = self.ui
        self._apply_context(ui._revert, ui.context)
        self._apply_context(ui._revert, ui._context)
        self.revert.setEnabled(False)
        ui.handler.revert(ui.info) 
        ui.modified = False
