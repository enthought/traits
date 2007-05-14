#-------------------------------------------------------------------------------
#
#  Written by: David C. Morrill
#
#  Date: 09/27/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#
#-------------------------------------------------------------------------------
""" Defines an editor that allows the user to used to debug UI-related problems.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Bool
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
    
from enthought.pyface.python_shell \
    import PythonShell
                                      
#-------------------------------------------------------------------------------
#  'ShellEditor' class:
#-------------------------------------------------------------------------------
                               
class ShellEditor ( Editor ):
    """ Editor that displays an interactive Python shell.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Is the shell editor is scrollable? This value overrides the default.
    scrollable = True 
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        locals = None
        value  = self.value
        if self.factory.share and isinstance( value, dict ):
            locals = value
        self._shell  = shell = PythonShell( parent, locals = locals )
        self.control = shell.control
        self.context_object.on_trait_change( self._update_editor, 
                                self.extended_name, remove = True )
        if locals is None:
            object = self.object
            shell.bind( 'self', object )
            shell.on_trait_change( self.update_object, 'command_executed',
                                   dispatch = 'ui' )
            if not isinstance( value, dict ):
                object.on_trait_change( self.update_any, dispatch = 'ui' )
            else:
                self._base_locals = locals = {}
                for name in self.control.interp.locals.keys():
                    locals[ name ] = None
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        locals      = self.control.interp.locals
        base_locals = self._base_locals
        if base_locals is None:
            object = self.object
            for name in object.trait_names():
                if name in locals:
                    try:
                        setattr( object, name, locals[ name ] )
                    except:
                        pass
        else:
            dic = self.value
            for name in locals.keys():
                if name not in base_locals:
                    try:
                        dic[ name ] = locals[ name ]
                    except:
                        pass
                        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if not self.factory.share:
            locals      = self.control.interp.locals
            base_locals = self._base_locals
            if base_locals is None:
                object = self.object
                for name in object.trait_names():
                    locals[ name ] = getattr( object, name, None )
            else:
                dic = self.value
                for name, value in dic.items():
                    locals[ name ] = value
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_any ( self, object, name, old, new ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        locals = self.control.interp.locals
        if self._base_locals is None:
            locals[ name ] = new
        else:
            self.value[ name ] = new
        
    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( ShellEditor, self ).dispose()
        self._shell.on_trait_change( self.update_object, 'command_executed', 
                                     remove = True )
        if self._base_locals is None:
            self.object.on_trait_change( self.update_any, remove = True )

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the 
    #  editor:
    #---------------------------------------------------------------------------
            
    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the 
            editor.
        """
        control = self._shell.control
        try:
            control.history      = prefs.get( 'history', [] )
            control.historyIndex = prefs.get( 'historyIndex', -1 )
        except:
            pass
            
    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------
            
    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        control = self._shell.control
        return { 'history':      control.history, 
                 'historyIndex': control.historyIndex }

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for shell editors.
class ToolkitEditorFactory ( BasicEditorFactory ):
    
    # The class used to construct editor objects:
    klass = ShellEditor
    
    # Should the shell interpreter use the object value's dictionary?
    share = Bool( False )
                 
