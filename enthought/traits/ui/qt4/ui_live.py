#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Creates a PyQt user interface for a specified UI object, where the UI
    is "live", meaning that it immediately updates its underlying object(s).
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
    import DefaultTitle, WindowColor, screen_dy

from enthought.traits.ui.undo \
    import UndoHistory
    
from enthought.traits.ui.menu \
    import UndoButton, RevertButton, OKButton, CancelButton, HelpButton

#-------------------------------------------------------------------------------
#  Creates a 'live update' PyQt user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_live ( ui, parent ):
    """ Creates a live, non-modal PyQt user interface for a specified UI
    object.
    """
    ui_dialog( ui, parent, False )

def ui_livemodal ( ui, parent ):
    """ Creates a live, modal PyQt user interface for a specified UI object.
    """
    ui_dialog( ui, parent, True )

def ui_dialog ( ui, parent, is_modal ):
    """ Creates a live PyQt user interface for a specified UI object.
    """
    if ui.owner is None:
        ui.owner = LiveWindow()
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
#  'LiveWindow' class:
#-------------------------------------------------------------------------------
    
class LiveWindow ( BaseDialog ):
    """ User interface window that immediately updates its underlying object(s).
    """
    
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------
    
    def init ( self, ui, parent, is_modal ):
        view = ui.view
        history = ui.history
        window = ui.control

        layout = QtGui.QVBoxLayout()

        if not view.resizable:
            layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)

        if window is not None:
            if history is not None:
                history.on_trait_change( self._on_undoable, 'undoable',
                                         remove = True )
                history.on_trait_change( self._on_redoable, 'redoable',
                                         remove = True )
                history.on_trait_change( self._on_revertable, 'undoable',
                                         remove = True )
            ui.reset()
        else:
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

        buttons = [ self.coerce_button( button ) for button in view.buttons ]
        nbuttons    = len( buttons )
        no_buttons  = ((nbuttons == 1) and self.is_button( buttons[0], '' ))
        has_buttons = ((not no_buttons) and ((nbuttons > 0) or view.undo or
                                         view.revert or view.ok or view.cancel))
        if has_buttons or (view.menubar is not None):
            if history is None:
                history = UndoHistory()
        else:
            history = None
        ui.history = history
        
        # Create the actual trait sheet panel and imbed it in a scrollable 
        # window (if requested):
        if ui.scrollable:
            sw = QtGui.QScrollArea()
            layout.addWidget(sw)
            sw.setWidget(panel(ui, sw))
        else:
            layout.addWidget(panel(ui, window))

        # Check to see if we need to add any of the special function buttons:
        if (not no_buttons) and (has_buttons or view.help):
            bbox = QtGui.QDialogButtonBox()
            
            # Convert all button flags to actual button actions if no buttons
            # were specified in the 'buttons' trait:
            if nbuttons == 0:
                if view.undo:
                    self.check_button( buttons, UndoButton )
                if view.revert:
                    self.check_button( buttons, RevertButton )
                if view.ok:
                    self.check_button( buttons, OKButton )
                if view.cancel:
                    self.check_button( buttons, CancelButton )
                if view.help:
                    self.check_button( buttons, HelpButton )
                
            # Create a button for each button action:
            for button in buttons:
                button = self.coerce_button(button)

                if self.is_button(button, 'Undo'):
                    self.undo = self.add_button(button, bbox,
                            QtGui.QDialogButtonBox.ActionRole, self._on_undo,
                            False)
                    history.on_trait_change(self._on_undoable, 'undoable',
                            dispatch='ui')
                    if history.can_undo:
                        self._on_undoable(True)

                    self.redo = self.add_button(button,bbox, 
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

            layout.addStretch(1)
            layout.addWidget(bbox)
        
        # Add the menu bar and tool bar (if any):
        self.add_menubar()
        self.add_toolbar()

        window.setLayout(layout)

    #---------------------------------------------------------------------------
    #  Closes the dialog window:
    #---------------------------------------------------------------------------
            
    def close ( self, rc ):            
        """ Closes the dialog window.
        """
        save_window(self.ui)
        self.ui.finish(rc)
        self.ui = self.undo = self.redo = self.revert = self.control = None

    #---------------------------------------------------------------------------
    #  Handles the user finishing with the dialog:
    #---------------------------------------------------------------------------
 
    def _on_finished ( self, result ):
        """ Handles the user finishing with the dialog.
        """
        accept = bool(result)

        if self.ui.handler.close(self.ui.info, accept):
            if not accept:
                self._on_revert()

            self.close(accept)

    #---------------------------------------------------------------------------
    #  Handles an 'Undo' change request:
    #---------------------------------------------------------------------------
           
    def _on_undo ( self ):
        """ Handles an "Undo" change request.
        """
        self.ui.history.undo()
   
    #---------------------------------------------------------------------------
    #  Handles a 'Redo' change request:
    #---------------------------------------------------------------------------
           
    def _on_redo ( self ):
        """ Handles a "Redo" change request.
        """
        self.ui.history.redo()
   
    #---------------------------------------------------------------------------
    #  Handles a 'Revert' all changes request:
    #---------------------------------------------------------------------------
           
    def _on_revert ( self ):
        """ Handles a request to revert all changes.
        """
        ui = self.ui
        ui.history.revert()
        ui.handler.revert( ui.info )
   
    #---------------------------------------------------------------------------
    #  Handles editing errors:
    #---------------------------------------------------------------------------
                        
    def _on_error ( self, errors ):
        """ Handles editing errors.
        """
        self.ok.Enable( errors == 0 )
    
    #---------------------------------------------------------------------------
    #  Handles the 'Help' button being clicked:
    #---------------------------------------------------------------------------
           
    def _on_help ( self, event ):
        """ Handles the 'user clicking the Help button.
        """
        self.ui.handler.show_help( self.ui.info, event.GetEventObject() )
            
    #---------------------------------------------------------------------------
    #  Handles the undo history 'undoable' state changing:
    #---------------------------------------------------------------------------
            
    def _on_undoable ( self, state ):
        """ Handles a change to the "undoable" state of the undo history 
        """
        self.undo.Enable( state )
            
    #---------------------------------------------------------------------------
    #  Handles the undo history 'redoable' state changing:
    #---------------------------------------------------------------------------
            
    def _on_redoable ( self, state ):
        """ Handles a change to the "redoable state of the undo history.
        """
        self.redo.Enable( state )
            
    #---------------------------------------------------------------------------
    #  Handles the 'revert' state changing:
    #---------------------------------------------------------------------------
            
    def _on_revertable ( self, state ):
        """ Handles a change to the "revert" state.
        """
        self.revert.Enable( state )
