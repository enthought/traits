#-------------------------------------------------------------------------------
#
#  Written by: David C. Morrill
#
#  Date: 03/02/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines an editor for playing animated GIF files.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from wx.animate \
    import Animation, AnimationCtrl
    
from enthought.traits.api \
    import Bool, Str
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
                                      
#-------------------------------------------------------------------------------
#  '_AnimatedGIFEditor' class:
#-------------------------------------------------------------------------------
                               
class _AnimatedGIFEditor ( Editor ):
    """ Editor that displays an animated GIF file.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Is the animated GIF file currently playing?
    playing = Bool( True )
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._animate = Animation( self.value )
        self.control  = AnimationCtrl( parent, -1, self._animate )
        self.control.SetUseWindowBackgroundColour()
        self.sync_value( self.factory.playing, 'playing', 'from' )
        self.set_tooltip()
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if not self.playing:
            self.control.Stop()
            
        self.control.LoadFile( self.value )
        self._file_loaded = True
        
        if self.playing:
            self.control.Play()

    #---------------------------------------------------------------------------
    #  Handles the editor 'playing' trait being changed:  
    #---------------------------------------------------------------------------
    
    def _playing_changed ( self ):
        if self._file_loaded:
            if self.playing:
                self.control.Play()
            else:
                self.control.Stop()
                    
#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for animated GIF editors:
class AnimatedGIFEditor ( BasicEditorFactory ):
    
    # The editor class to be created:
    klass = _AnimatedGIFEditor
    
    # The optional trait used to control whether the animated GIF file is 
    # playing or not:
    playing = Str
                 
