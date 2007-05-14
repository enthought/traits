#-------------------------------------------------------------------------------
#  
#  Traits UI Windows specific Flash editor.  
#  
#  Written by: David C. Morrill
#  
#  Date: 03/11/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Traits UI MS Flash editor. """

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import  wx

if wx.Platform == '__WXMSW__':
    from wx.lib.flashwin import FlashWindow
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory

#-------------------------------------------------------------------------------
#  '_FlashEditor' class:
#-------------------------------------------------------------------------------
                               
class _FlashEditor ( Editor ):
    """ Traits UI Flash editor.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Is the table editor is scrollable? This value overrides the default.
    scrollable = True
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = FlashWindow( parent )
        self.set_tooltip()
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.str_value.strip()
        if value.find( '://' ) < 0:
            value = 'file://' + value
            
        wx.BeginBusyCursor()
        self.control.LoadMovie( 0, value )
        wx.EndBusyCursor()
                    
#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for Flash editors:
class FlashEditor ( BasicEditorFactory ):
    
    # The editor class to be created:
    klass = _FlashEditor

