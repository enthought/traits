#-------------------------------------------------------------------------------
#
#  Traits UI 'display only' LED numeric editor.
#
#  Written by: David C. Morrill
#
#  Date: 03/02/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Traits UI 'display only' LED numeric editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from wx.gizmos \
    import LEDNumberCtrl, LED_ALIGN_LEFT, LED_ALIGN_CENTER, LED_ALIGN_RIGHT
    
from enthought.traits.api \
    import Enum
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
 
#-------------------------------------------------------------------------------
#  Constants:  
#-------------------------------------------------------------------------------
        
# LED alignment styles:
LEDStyles = {
    'left':   LED_ALIGN_LEFT,
    'center': LED_ALIGN_CENTER,
    'right':  LED_ALIGN_RIGHT,
}

#-------------------------------------------------------------------------------
#  '_LEDEditor' class:
#-------------------------------------------------------------------------------
                               
class _LEDEditor ( Editor ):
    """ Traits UI 'display only' LED numeric editor.
    """
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = LEDNumberCtrl( parent, -1 ) 
        self.control.SetAlignment( LEDStyles[ self.factory.alignment ] )
        self.set_tooltip()
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.SetValue( self.str_value )
                    
#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for LED editors:
class LEDEditor ( BasicEditorFactory ):
    
    # The editor class to be created:
    klass = _LEDEditor
    
    # The alignment of the numeric text within the control:
    alignment = Enum( 'right', 'left', 'center' )
                 
