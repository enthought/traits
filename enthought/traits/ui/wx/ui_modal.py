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
# Symbols defined: ui_modal
#
#------------------------------------------------------------------------------
""" Creates a wxPython user interface for a specified UI object.
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
    import DefaultTitle, WindowColor, screen_dy, scrollbar_dx
    
from enthought.traits.ui.menu \
    import ApplyButton, RevertButton, OKButton, CancelButton, HelpButton

#-------------------------------------------------------------------------------
#  Creates a modal wxPython user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_modal ( ui, parent ):
    """ Creates a modal wxPython user interface for a specified UI object.
    """
    ui_dialog( ui, parent, True )

#-------------------------------------------------------------------------------
#  Creates a non-modal wxPython user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_nonmodal ( ui, parent ):
    """ Creates a non-modal wxPython user interface for a specified UI object.
    """
    ui_dialog( ui, parent, False )

#-------------------------------------------------------------------------------
#  Creates a wxPython dialog-based user interface for a specified UI object:
#-------------------------------------------------------------------------------

def ui_dialog ( ui, parent, is_modal ):
    """ Creates a wxPython dialog box for a specified UI object.
    
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
        style         = 0
        view          = ui.view
        if view.resizable:
            style |= wx.RESIZE_BORDER
        title = view.title
        if title == '':
            title = DefaultTitle
          
        revert = apply = False
        window = ui.control
        if window is not None:
            window.SetSizer( None )
            ui.reset()
            if hasattr( self, 'revert' ):
                revert = self.revert.IsEnabled()
            if hasattr( self, 'apply' ):
                apply = self.apply.IsEnabled()
        else:
            self.ui = ui
            if is_modal:
                window = wx.Dialog( parent, -1, title, 
                                    style = style | wx.DEFAULT_DIALOG_STYLE )
            else:
                window = wx.Frame(  parent, -1, title, style = style |
                            (wx.DEFAULT_FRAME_STYLE & (~wx.RESIZE_BORDER) ) )
                window.SetBackgroundColour( WindowColor )
            self.control = window
            self.set_icon( view.icon )
            wx.EVT_CLOSE( window, self._on_close_page )
            wx.EVT_CHAR(  window, self._on_key )
            
            # Create the 'context' copies we will need while editing:
            context     = ui.context
            ui._context = context
            ui.context  = self._copy_context( context )
            ui._revert  = self._copy_context( context )
        
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
        
        buttons  = [ self.coerce_button( button ) for button in view.buttons ]
        nbuttons = len( buttons )
        if (nbuttons != 1) or (not self.is_button( buttons[0], '' )):
            
            # Create the necessary special function buttons:
            sw_sizer.Add( wx.StaticLine( window, -1 ), 0, wx.EXPAND )
            b_sizer = wx.BoxSizer( wx.HORIZONTAL )
            
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
                if self.is_button( button, 'Apply' ):
                    self.apply = self.add_button( button, b_sizer, 
                                                  self._on_apply, apply )
                    ui.on_trait_change( self._on_applyable, 'modified',
                                        dispatch = 'ui' )
                elif self.is_button( button, 'Revert' ):
                    self.revert = self.add_button( button, b_sizer, 
                                                   self._on_revert, revert )
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
        window.SetSizerAndFit( sw_sizer )

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
    #  Handles the user clicking the window/dialog 'close' button/icon:
    #---------------------------------------------------------------------------
 
    def _on_close_page ( self, event ):
        """ Handles the user clicking the window/dialog "close" button/icon.
        """
        if self.ui.view.close_result == True:
            self._on_ok( event )
        else:
            self._on_cancel( event )

    #---------------------------------------------------------------------------
    #  Closes the window and saves changes (if allowed by the handler):
    #---------------------------------------------------------------------------
 
    def _on_ok ( self, event = None ):
        """ Closes the window and saves changes (if allowed by the handler).
        """
        if self.ui.handler.close( self.ui.info, True ):
            self._apply_context( self.ui.context, self.ui._context )
            self.close( wx.ID_OK )

    #---------------------------------------------------------------------------
    #  Closes the window and discards changes (if allowed by the handler):
    #---------------------------------------------------------------------------
 
    def _on_cancel ( self, event = None ):
        """ Closes the window and discards changes (if allowed by the handler).
        """
        if self.ui.handler.close( self.ui.info, False ):
            self._apply_context( self.ui._revert, self.ui._context )
            self.close( wx.ID_CANCEL )
    
    #---------------------------------------------------------------------------
    #  Handles the 'Help' button being clicked:
    #---------------------------------------------------------------------------
           
    def _on_help ( self, event ):
        """ Handles the **Help** button being clicked.
        """
        self.ui.handler.show_help( self.ui.info, event.GetEventObject() )
 
    #---------------------------------------------------------------------------
    #  Handles the user hitting the 'Esc'ape key:
    #---------------------------------------------------------------------------
 
    def _on_key ( self, event ):
        """ Handles the user pressing the Escape key.
        """
        if event.GetKeyCode() == 0x1B:
           self._on_close_page( event )
   
    #---------------------------------------------------------------------------
    #  Handles an 'Apply' all changes request:
    #---------------------------------------------------------------------------
           
    def _on_apply ( self, event ):
        """ Handles a request to apply changes.
        """
        ui = self.ui
        self._apply_context( ui.context, ui._context )
        self.revert.Enable( True )
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
        self.revert.Enable( False )
        ui.handler.revert( ui.info ) 
        ui.modified = False
            
    #---------------------------------------------------------------------------
    #  Handles the user interface 'modified' state changing:
    #---------------------------------------------------------------------------
            
    def _on_applyable ( self, state ):
        """ Handles a change to the "modified" state of the user interface .
        """
        self.apply.Enable( state )
            
    #---------------------------------------------------------------------------
    #  Handles editing errors:
    #---------------------------------------------------------------------------
                        
    def _on_error ( self, errors ):
        """ Handles editing errors.
        """
        self.ok.Enable( errors == 0 )
               
