#-------------------------------------------------------------------------------
#
#  Written by: David C. Morrill
#
#  Date: 05/20/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#
#-------------------------------------------------------------------------------
""" Defines the key binding editor for use with the KeyBinding class. This is a 
specialized editor used to associate a particular key with a control (i.e., the
key binding editor).
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import Trait, TraitError, HasStrictTraits, Str, List, Any, Instance, \
           Event, false

from enthought.traits.ui.api \
    import View, Item, ListEditor

from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
    
from enthought.util.wx.dialog \
    import confirmation
    
from key_event_to_name \
    import key_event_to_name
                                      
#-------------------------------------------------------------------------------
#  'KeyBindingEditor' class:
#-------------------------------------------------------------------------------
                               
class KeyBindingEditor ( Editor ):
    """ An editor for modifying bindings of keys to controls.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Does the editor's control have focus currently?
    has_focus = false
    
    # Keyboard event
    key = Event
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = KeyBindingCtrl( self, parent )
        self.control.SetSize( wx.Size( 160, 19 ) )

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        try:
            self.value = value = key_event_to_name( event )
            self._binding.text = value
        except:
            pass
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self.control.Refresh()
            
    #---------------------------------------------------------------------------
    #  Updates the current focus setting of the control:  
    #---------------------------------------------------------------------------
    
    def update_focus ( self, has_focus ):
        """ Updates the current focus setting of the control.
        """
        if has_focus:
            self._binding.border_size     = 1
            self.object.owner.focus_owner = self._binding
        
    #---------------------------------------------------------------------------
    #  Handles a keyboard event:   
    #---------------------------------------------------------------------------
    
    def _key_changed ( self, event ):
        """ Handles a keyboard event.
        """
        binding     = self.object
        key_name    = key_event_to_name( event )
        cur_binding = binding.owner.key_binding_for( binding, key_name )
        if cur_binding is not None:
            if confirmation( None, 
                     "'%s' has already been assigned to '%s'.\n"
                     "Do you wish to continue?" % ( 
                     key_name, cur_binding.description ),
                     'Duplicate Key Definition' ) == 5104:
                return
                
        self.value = key_name

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------
                
ToolkitEditorFactory = BasicEditorFactory( klass = KeyBindingEditor )
        
#-------------------------------------------------------------------------------
#  'KeyBindingCtrl' class:
#-------------------------------------------------------------------------------

class KeyBindingCtrl ( wx.Window ):
    """ wxPython control for editing key bindings.
    """
    #---------------------------------------------------------------------------
    #  Initialize the object:
    #---------------------------------------------------------------------------
    
    def __init__ ( self, editor, parent, wid = -1, pos = wx.DefaultPosition,
                   size = wx.DefaultSize ):
                       
        super( KeyBindingCtrl, self ).__init__( parent, wid, pos, size,
                                                style = wx.CLIP_CHILDREN |
                                                        wx.WANTS_CHARS )
        # Save the reference to the controlling editor object:                                                        
        self.editor = editor
        
        # Indicate we don't have the focus right now:
        editor.has_focus = False

        # Set up the 'erase background' event handler:
        wx.EVT_ERASE_BACKGROUND( self, self._on_erase_background )
 
        # Set up the 'paint' event handler:
        wx.EVT_PAINT( self, self._paint )
        
        # Set up the focus change handlers:
        wx.EVT_SET_FOCUS(  self, self._get_focus )
        wx.EVT_KILL_FOCUS( self, self._lose_focus )
        
        # Set up mouse event handlers:
        wx.EVT_LEFT_DOWN( self, self._set_focus )
        
        # Handle key events:
        wx.EVT_CHAR( self, self._on_char )
 
    #---------------------------------------------------------------------------
    #  Handle keyboard keys being pressed:
    #---------------------------------------------------------------------------
           
    def _on_char ( self, event ):
        """ Handle keyboard keys being pressed.
        """
        self.editor.key = event
   
    #---------------------------------------------------------------------------
    #  Erase background event handler:
    #---------------------------------------------------------------------------

    def _on_erase_background ( self, event ):
        pass
    
    #---------------------------------------------------------------------------
    #  Do a GUI toolkit specific screen update:
    #---------------------------------------------------------------------------

    def _paint ( self, event ):
        """ Updates the screen.
        """
        wdc    = wx.PaintDC( self )
        dx, dy = self.GetSizeTuple()
        if self.editor.has_focus:
            wdc.SetPen( wx.Pen( wx.RED, 2 ) )
            wdc.DrawRectangle( 1, 1, dx - 1, dy - 1 )
        else:
            wdc.SetPen( wx.Pen( wx.BLACK ) )
            wdc.DrawRectangle( 0, 0, dx, dy )
        wdc.DrawText( self.editor.str_value, 5, 1 )
            
    #---------------------------------------------------------------------------
    #  Sets the keyboard focus to this window:  
    #---------------------------------------------------------------------------
                        
    def _set_focus ( self, event ):
        """ Sets the keyboard focus to this window.
        """
        self.SetFocus()
        
    #---------------------------------------------------------------------------
    #  Handles getting/losing the focus:
    #---------------------------------------------------------------------------
    
    def _get_focus ( self, event ):
        """ Handles getting the focus.
        """
        self.editor.has_focus = True
        self.Refresh()
        
    def _lose_focus ( self, event ):  
        """ Handles losing the focus.
        """
        self.editor.has_focus = False
        self.Refresh()

