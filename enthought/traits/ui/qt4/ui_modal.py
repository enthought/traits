#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Creates a PyQt user interface for a specified UI object.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

from helper \
    import restore_window, save_window
    
from ui_base \
    import BaseDialog
    
from ui_panel \
    import panel, show_help
    
from constants \
    import DefaultTitle
    
from enthought.traits.ui.menu \
    import ApplyButton, RevertButton, OKButton, CancelButton, HelpButton

#-------------------------------------------------------------------------------
#  Creates a modal PyQt user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_modal ( ui, parent ):
    """ Creates a modal PyQt user interface for a specified UI object.
    """
    ui_dialog( ui, parent, True )

#-------------------------------------------------------------------------------
#  Creates a non-modal PyQt user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_nonmodal ( ui, parent ):
    """ Creates a non-modal PyQt user interface for a specified UI object.
    """
    ui_dialog( ui, parent, False )

#-------------------------------------------------------------------------------
#  Creates a PyQt dialog-based user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_dialog ( ui, parent, is_modal ):
    """ Creates a PyQt dialog box for a specified UI object.
    
    Changes are not immediately applied to the underlying object. The user must
    click **Apply** or **OK** to apply changes. The user can revert changes by
    clicking **Revert** or **Cancel**.
    """
    if ui.owner is None:
        ui.owner = ModalDialog()
    ui.owner.init( ui, parent, is_modal )
    ui.control = ui.owner.control
    ui.control._parent = parent
    try:
        ui.prepare_ui()
    except:
        ui.control.deleteLater()
        ui.control.ui = None
        ui.control    = None
        ui.owner      = None
        ui.result     = False
        raise
    ui.handler.position( ui.info )
    restore_window( ui )
    if is_modal:
        ui.control.exec_()
    else:
        ui.control.show()
    
#-------------------------------------------------------------------------------
#  'ModalDialog' class:
#-------------------------------------------------------------------------------
    
class ModalDialog ( BaseDialog ):
    """ Modal dialog box for Traits-based user interfaces.
    """
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------
    
    def init ( self, ui, parent, is_modal ):
        self.is_modal = is_modal
        view = ui.view

        revert = apply = False
        window = ui.control
        if window is not None:
            layout = window.layout()

            ui.reset()
            if hasattr( self, 'revert' ):
                revert = self.revert.isEnabled()
            if hasattr( self, 'apply' ):
                apply = self.apply.isEnabled()
        else:
            layout = None

            self.ui = ui

            flags = QtCore.Qt.WindowSystemMenuHint
            if view.resizable:
                flags |= QtCore.Qt.WindowMinMaxButtonsHint
            else:
                flags |= QtCore.Qt.MSWindowsFixedSizeDialogHint

            window = QtGui.QDialog(parent, flags)

            window.setModal(is_modal)

            if view.title != '':
                window.setWindowTitle(view.title)
            else:
                window.setWindowTitle(DefaultTitle)

            window.connect(window, QtCore.SIGNAL('finished(int)'),
                self._on_finished)

            self.control = window
            self.set_icon( view.icon )

            # Create the 'context' copies we will need while editing:
            context     = ui.context
            ui._context = context
            ui.context  = self._copy_context( context )
            ui._revert  = self._copy_context( context )

        if layout is None:
            layout = QtGui.QVBoxLayout(window)

        if not view.resizable:
            layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        
        # Create the actual trait sheet panel and imbed it in a scrollable 
        # window (if requested):
        if ui.scrollable:
            sw = QtGui.QScrollArea()
            layout.addWidget(sw)
            pan = panel(ui, sw)
            sw.setWidget(pan)
        else:
            pan = panel(ui, window)
            layout.addWidget(pan)

        # Remove any margin from the panel so that it lines up with the
        # buttons.
        pan.layout().setMargin(0)

        buttons  = [ self.coerce_button( button ) for button in view.buttons ]
        nbuttons = len( buttons )
        if (nbuttons != 1) or (not self.is_button( buttons[0], '' )):
            bbox = QtGui.QDialogButtonBox()

            # Create the necessary special function buttons:
            if nbuttons == 0:
                if view.apply:
                    self.check_button( buttons, ApplyButton )
                    if view.revert:
                        self.check_button( buttons, RevertButton )
                if view.ok:
                    self.check_button( buttons, OKButton )
                if view.cancel:
                    self.check_button( buttons, CancelButton )
                if view.help:
                    self.check_button( buttons, HelpButton )
                    
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
                            QtGui.QDialogButtonBox.AcceptRole, window.accept)
                    ui.on_trait_change(self._on_error, 'errors', dispatch='ui')

                elif self.is_button(button, 'Cancel'):
                    self.add_button(button, bbox,
                            QtGui.QDialogButtonBox.RejectRole, window.reject)

                elif self.is_button(button, 'Help'):
                    self.add_button(button, bbox,
                            QtGui.QDialogButtonBox.HelpRole, self._on_help)

                elif not self.is_button(button, ''):
                    self.add_button(button, bbox,
                            QtGui.QDialogButtonBox.ActionRole)
                    
            layout.addWidget(bbox)
        
        # Add the menu bar and tool bar (if any):
        self.add_menubar()
        self.add_toolbar()

    #---------------------------------------------------------------------------
    #  Closes the dialog window:
    #---------------------------------------------------------------------------
            
    def close ( self, rc ):            
        """ Closes the dialog window.
        """
        save_window(self.ui)
        self.ui.finish(rc)
        self.ui = self.apply = self.revert = self.help = self.control = None
        
    #---------------------------------------------------------------------------
    #  Creates a copy of a 'context' dictionary:
    #---------------------------------------------------------------------------
        
    def _copy_context ( self, context ):
        """ Creates a copy of a *context* dictionary.
        """
        result = {}
        for name, value in context.items():
            if value is not None:
                result[ name ] = value.clone_traits()
            else:
                result[ name ] = None
        return result
        
    #---------------------------------------------------------------------------
    #  Applies the traits in the 'from' context to the 'to' context:
    #---------------------------------------------------------------------------
        
    def _apply_context ( self, from_context, to_context ):
        """ Applies the traits in the *from_context* to the *to_context*.
        """
        for name, value in from_context.items():
            if value is not None:
                to_context[ name ].copy_traits( value )
            else:
                to_context[ name ] = None
        if to_context is self.ui._context:
            on_apply = self.ui.view.on_apply
            if on_apply is not None:
                on_apply()

    #---------------------------------------------------------------------------
    #  Handles the user finishing with the dialog:
    #---------------------------------------------------------------------------

    def _on_finished ( self, result ):
        """ Handles the user finishing with the dialog.
        """
        accept = bool(result)

        if self.ui.handler.close(self.ui.info, accept):
            if accept:
                self._apply_context(self.ui.context, self.ui._context)
            else:
                self._apply_context(self.ui._revert, self.ui._context)

            self.close(accept)

    #---------------------------------------------------------------------------
    #  Handles the 'Help' button being clicked:
    #---------------------------------------------------------------------------
           
    def _on_help ( self, event ):
        """ Handles the **Help** button being clicked.
        """
        self.ui.handler.show_help( self.ui.info, event.GetEventObject() )
 
    #---------------------------------------------------------------------------
    #  Handles an 'Apply' all changes request:
    #---------------------------------------------------------------------------
           
    def _on_apply ( self, event ):
        """ Handles a request to apply changes.
        """
        ui = self.ui
        self._apply_context( ui.context, ui._context )
        self.revert.setEnable( True )
        ui.handler.apply( ui.info )
        ui.modified = False
   
    #---------------------------------------------------------------------------
    #  Handles a 'Revert' all changes request:
    #---------------------------------------------------------------------------
           
    def _on_revert ( self, event ):
        """ Handles a request to revert changes.
        """
        ui = self.ui
        self._apply_context( ui._revert, ui.context )
        self._apply_context( ui._revert, ui._context )
        self.revert.setEnable( False )
        ui.handler.revert( ui.info ) 
        ui.modified = False
            
    #---------------------------------------------------------------------------
    #  Handles the user interface 'modified' state changing:
    #---------------------------------------------------------------------------
            
    def _on_applyable ( self, state ):
        """ Handles a change to the "modified" state of the user interface .
        """
        self.apply.setEnable( state )
            
    #---------------------------------------------------------------------------
    #  Handles editing errors:
    #---------------------------------------------------------------------------
                        
    def _on_error ( self, errors ):
        """ Handles editing errors.
        """
        self.ok.setEnable( errors == 0 )
