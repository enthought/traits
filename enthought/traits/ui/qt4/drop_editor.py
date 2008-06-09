#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines a drop target editor and editor factory for the PyQt user interface
    toolkit. A drop target editor handles drag and drop operations as a drop
    target.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtGui

from enthought.traits.api \
    import Any, Bool
    
from text_editor \
    import SimpleEditor as Editor
    
from text_editor \
    import ToolkitEditorFactory as EditorFactory
    
from constants \
    import DropColor

from clipboard \
    import PyMimeData

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for drop editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Allowable drop objects must be of this class (optional)
    klass = Any
    
    # Must allowable drop objects be bindings?
    binding = Bool(False)
    
    # Can the user type into the editor, or is it read only?
    readonly = Bool(True)
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
    
    def custom_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
    
    def text_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self, 
                             ui          = ui, 
                             object      = object, 
                             name        = name, 
                             description = description ) 
                                      
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( Editor ):
    """ Simple style of drop editor, which displays a read-only text field that
    contains the string representation of the object trait's value.
    """
    
    # Background color when it is OK to drop objects.
    ok_color = DropColor
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        if self.factory.readonly:
            self.control = QtGui.QLineEdit(self.str_value)
            self.control.setReadOnly(True)
            self.set_tooltip()
        else:
            super( SimpleEditor, self ).init( parent )

        pal = QtGui.QPalette(self.control.palette())
        pal.setColor(QtGui.QPalette.Base, self.ok_color)
        self.control.setPalette(pal)

        # Patch the type of the control to insert the DND event handlers.
        self.control.__class__ = type(_DropWidget.__name__,
                (type(self.control), ), dict(_DropWidget.__dict__))

        self.control._qt4_editor = self

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified object trait value:
    #---------------------------------------------------------------------------
  
    def string_value ( self, value ):
        """ Returns the text representation of a specified object trait value.
        """
        if value is None:
            return ''
        return str( value )
        
    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------
        
    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        pass


class _DropWidget(object):

    #---------------------------------------------------------------------------
    #  Handles a Python object being dropped on the control:    
    #---------------------------------------------------------------------------

    def dropEvent(self, e):
        """ Handles a Python object being dropped on the tree.
        """
        editor = self._qt4_editor

        klass = editor.factory.klass

        if editor.factory.binding:
            value = getattr(clipboard, 'node', None)
        else:
            value = e.mimeData().instance()

        if (klass is None) or isinstance(data, klass):
            editor._no_update = True
            try:
                if hasattr( value, 'drop_editor_value' ):
                    editor.value = value.drop_editor_value()
                else:
                    editor.value = value
                if hasattr( value, 'drop_editor_update' ):
                    value.drop_editor_update(self)
                else:
                    self.setText(editor.str_value)
            finally:
                editor._no_update = False 

            e.acceptProposedAction()

    #---------------------------------------------------------------------------
    #  Handles a Python object being dragged over the control:    
    #---------------------------------------------------------------------------
                
    def dragEnterEvent(self, e):
        """ Handles a Python object being dragged over the tree.
        """
        editor = self._qt4_editor

        if editor.factory.binding:
            data = getattr(clipboard, 'node', None)
        else:
            md = e.mimeData()

            if not isinstance(md, PyMimeData):
                return

            data = md.instance()

        try:
            editor.object.base_trait(editor.name).validate(editor.object,
                    editor.name, data)
            e.acceptProposedAction()
        except:
            pass
