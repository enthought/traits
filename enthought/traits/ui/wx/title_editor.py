#-------------------------------------------------------------------------------
#
#  Define an editor that displays a string value as a title. 
#
#  Written by: David C. Morrill
#
#  Date: 07/06/2006
#
#  (c) Copyright 2006 by David C. Morrill
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------
    
from enthought.traits.api \
    import Str
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
    
from enthought.pyface.heading_text \
    import HeadingText
                                      
#-------------------------------------------------------------------------------
#  '_TitleEditor' class:
#-------------------------------------------------------------------------------
                               
class _TitleEditor ( Editor ):
    
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._control = HeadingText( parent )
        self.control  = self._control.control
        self.set_tooltip()
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        self._control.text = self.str_value

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------
                
TitleEditor = BasicEditorFactory( klass = _TitleEditor )
                 
