#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: David C. Morrill
# Date: 11/01/2004
#
#  Symbols defined: ui_live
#
#------------------------------------------------------------------------------
""" Creates a wxPython user interface for a specified UI object, where the UI
is "live", meaning that it immediately updates its underlying object(s).
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from helper \
    import restore_window, save_window
    
from ui_base \
    import BaseDialog
    
from ui_panel \
    import panel, show_help
    
from constants \
    import DefaultTitle, WindowColor, screen_dy, \
                                     scrollbar_dx
from enthought.traits.ui.undo \
    import UndoHistory
    
from enthought.traits.ui.menu \
    import UndoButton, RevertButton, OKButton, CancelButton, HelpButton

#-------------------------------------------------------------------------------
#  Creates a 'live update' wxPython user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_live ( ui, parent ):
    """ Creates a live, non-modal wxPython user interface for a specified UI
    object.
    """
    ui_dialog( ui, parent, False )

def ui_livemodal ( ui, parent ):
    """ Creates a live, modal wxPython user interface for a specified UI object.
    """
    ui_dialog( ui, parent, True )

def ui_dialog ( ui, parent, is_modal ):
    """ Creates a live wxPython user interface for a specified UI object.
    """
    if ui.owner is None:
        ui.owner = LiveWindow()
    ui.owner.init( ui, parent, is_modal )
    ui.control = ui.owner.control
    ui.control._parent = parent
    try:
        ui.prepare_ui()
    except:
        ui.control.Destroy()
        ui.control.ui = None
        ui.control    = None
        ui.owner      = None
        ui.result     = False
        raise
    ui.handler.position( ui.info )
    restore_window( ui )
    if is_modal:
        ui.control.ShowModal()
    else:
        ui.control.Show()
    
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
        self.is_modal = is_modal
        style         = 0
        view          = ui.view
        if view.resizable:
            style |= wx.RESIZE_BORDER
        title = view.title
        if title == '':
            title = DefaultTitle
        history = ui.history
        window  = ui.control
        if window is not None:
            if history is not None:
                history.on_trait_change( self._on_undoable, 'undoable',
                                         remove = True )
                history.on_trait_change( self._on_redoable, 'redoable',
                                         remove = True )
                history.on_trait_change( self._on_revertable, 'undoable',
                                         remove = True )
            window.SetSizer( None )
            ui.reset()
        else:
            self.ui = ui
            if is_modal:
                if view.resizable:
                    style |= (wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
                window = wx.Dialog( parent, -1, title,
                                    style = style | wx.DEFAULT_DIALOG_STYLE )
            else:
                if parent is not None:
                    style |= wx.FRAME_FLOAT_ON_PARENT | wx.FRAME_NO_TASKBAR 
                window = wx.Frame(  parent, -1, title, style = style |
                               (wx.DEFAULT_FRAME_STYLE & (~wx.RESIZE_BORDER) ) )
                window.SetBackgroundColour( WindowColor )
            self.control = window
            self.set_icon( view.icon )
            wx.EVT_CLOSE( window, self._on_close_page )
            wx.EVT_CHAR(  window, self._on_key )
         
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
        sw_sizer = wx.BoxSizer( wx.VERTICAL )
        if ui.scrollable:
            sizer       = wx.BoxSizer( wx.VERTICAL )
            sw          = wx.ScrolledWindow( window )
            trait_sheet = panel( ui, sw )
            sizer.Add( trait_sheet, 1, wx.EXPAND | wx.ALL, 4 )
            tsdx, tsdy = trait_sheet.GetSizeTuple()
            tsdx += 8
            tsdy += 8
            sw.SetScrollRate( 16, 16 )
            max_dy = (2 * screen_dy) / 3
            sw.SetSizer( sizer )
            sw.SetSize( wx.Size( tsdx + ((tsdy > max_dy) * scrollbar_dx), 
                                 min( tsdy, max_dy ) ) )
        else:
            sw = panel( ui, window )
            
        sw_sizer.Add( sw, 1, wx.EXPAND )
        
        # Check to see if we need to add any of the special function buttons:
        if (not no_buttons) and (has_buttons or view.help):
            sw_sizer.Add( wx.StaticLine( window, -1 ), 0, wx.EXPAND )
            b_sizer = wx.BoxSizer( wx.HORIZONTAL )
            
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
                button = self.coerce_button( button )
                if self.is_button( button, 'Undo' ):
                    self.undo = self.add_button( button, b_sizer, 
                                                 self._on_undo, False )
                    self.redo = self.add_button( button, b_sizer, 
                                                 self._on_redo, False, 'Redo' )
                    history.on_trait_change( self._on_undoable, 'undoable', 
                                             dispatch = 'ui' )
                    history.on_trait_change( self._on_redoable, 'redoable',
                                             dispatch = 'ui' )
                    if history.can_undo:
                        self._on_undoable( True )
                    if history.can_redo:
                        self._on_redoable( True )
                elif self.is_button( button, 'Revert' ): 
                    self.revert = self.add_button( button, b_sizer,
                                                   self._on_revert, False )
                    history.on_trait_change( self._on_revertable, 'undoable',
                                             dispatch = 'ui' )
                    if history.can_undo:
                        self._on_revertable( True )
                elif self.is_button( button, 'OK' ): 
                    self.ok = self.add_button( button, b_sizer, self._on_ok )
                    ui.on_trait_change( self._on_error, 'errors', 
                                        dispatch = 'ui' )
                elif self.is_button( button, 'Cancel' ): 
                    self.add_button( button, b_sizer, self._on_cancel )
                elif self.is_button( button, 'Help' ): 
                    self.add_button( button, b_sizer, self._on_help )
                elif not self.is_button( button, '' ):
                    self.add_button( button, b_sizer )
            sw_sizer.Add( b_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5 )
        
        # Add the menu bar and tool bar (if any):
        self.add_menubar()
        self.add_toolbar()
         
        # Lay all of the dialog contents out:
        window.SetSizer( sw_sizer )
        window.Fit()

    #---------------------------------------------------------------------------
    #  Closes the dialog window:
    #---------------------------------------------------------------------------
            
    def close ( self, rc = wx.ID_OK ):            
        """ Closes the dialog window.
        """
        ui = self.ui
        save_window( ui )
        if self.is_modal:
            self.control.EndModal( rc )
        ui.finish( rc == wx.ID_OK )
        self.ui = self.undo = self.redo = self.revert = self.control = None

    #---------------------------------------------------------------------------
    #  Handles the user clicking the window/dialog 'close' button/icon:
    #---------------------------------------------------------------------------
 
    def _on_close_page ( self, event ):
        """ Handles the user clicking the window/dialog "close" button/icon.
        """
        if self.ui.view.close_result == False:
            self._on_cancel( event )
        else:
            self._on_ok( event )

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'OK' button:
    #---------------------------------------------------------------------------
 
    def _on_ok ( self, event = None ):
        """ Handles the user clicking the **OK** button.
        """
        if self.ui.handler.close( self.ui.info, True ):
            self.close( wx.ID_OK )
               
    #---------------------------------------------------------------------------
    #  Handles the user hitting the 'Esc'ape key:
    #---------------------------------------------------------------------------
 
    def _on_key ( self, event ):
        """ Handles the user pressing the Escape key.
        """
        if event.GetKeyCode() == 0x1B:
           self._on_close_page( event )
   
    #---------------------------------------------------------------------------
    #  Handles an 'Undo' change request:
    #---------------------------------------------------------------------------
           
    def _on_undo ( self, event ):
        """ Handles an "Undo" change request.
        """
        self.ui.history.undo()
   
    #---------------------------------------------------------------------------
    #  Handles a 'Redo' change request:
    #---------------------------------------------------------------------------
           
    def _on_redo ( self, event ):
        """ Handles a "Redo" change request.
        """
        self.ui.history.redo()
   
    #---------------------------------------------------------------------------
    #  Handles a 'Revert' all changes request:
    #---------------------------------------------------------------------------
           
    def _on_revert ( self, event ):
        """ Handles a request to revert all changes.
        """
        ui = self.ui
        ui.history.revert()
        ui.handler.revert( ui.info )
   
    #---------------------------------------------------------------------------
    #  Handles a 'Cancel' all changes request:
    #---------------------------------------------------------------------------
           
    def _on_cancel ( self, event ):
        """ Handles a request to cancel all changes.
        """
        if self.ui.handler.close( self.ui.info, False ):
            self._on_revert( event )
            self.close( wx.ID_CANCEL )
            
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
           
