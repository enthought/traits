#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the base PyQt EditorFactory class and classes the various 
styles of editors used in a Traits-based user interface.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui
    
from enthought.traits.api \
    import TraitError, Any, Event, Str

from enthought.traits.ui.editor_factory \
    import EditorFactory as UIEditorFactory

from helper \
    import enum_values_changed

from editor \
    import Editor
    
#-------------------------------------------------------------------------------
#  'EditorFactory' base class:
#-------------------------------------------------------------------------------

class EditorFactory ( UIEditorFactory ):
    """ Base class for PyQt editor factories.
    """
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
        return self.simple_editor( ui, object, name, description, parent )
    
    def text_editor ( self, ui, object, name, description, parent ):
        return TextEditor( parent,
                           factory     = self, 
                           ui          = ui, 
                           object      = object, 
                           name        = name, 
                           description = description ) 
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return ReadonlyEditor( parent,
                               factory     = self, 
                               ui          = ui, 
                               object      = object, 
                               name        = name, 
                               description = description )
                               
#-------------------------------------------------------------------------------
#  'EditorWithListFactory' base class:
#-------------------------------------------------------------------------------

class EditorWithListFactory ( EditorFactory ):
    """ Base class for factories of editors for objects that contain lists.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Values to enumerate (can be a list, tuple, dict, or a CTrait or
    # TraitHandler that is "mapped"):
    values = Any 
    
    # Extended name of the trait on **object** containing the enumeration data:
    object = Str( 'object' )

    # Name of the trait on 'object' containing the enumeration data
    name = Str  

    # Fired when the **values** trait has been updated:
    values_modified = Event

    #---------------------------------------------------------------------------
    #  Recomputes the mappings whenever the 'values' trait is changed:
    #---------------------------------------------------------------------------

    def _values_changed ( self ):
        """ Recomputes the mappings whenever the **values** trait is changed.
        """
        self._names, self._mapping, self._inverse_mapping = \
            enum_values_changed( self.values )

        self.values_modified = True

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                        
class SimpleEditor ( Editor ):
    """ Base class for simple style editors, which displays a text field
    containing the text representation of the object trait value. Clicking in
    the text field displays an editor-specific dialog box for changing the
    value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = _SimpleField(self)
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #  
    #  (Normally overridden in a subclass)
    #---------------------------------------------------------------------------
 
    def popup_editor(self):
        """ Invokes the pop-up editor for an object trait.
        """
        pass

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor ( Editor ):
    """ Base class for text style editors, which displays an editable text 
    field, containing a text representation of the object trait value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QLineEdit(self.str_value)
        QtCore.QObject.connect(self.control,
                QtCore.SIGNAL('editingFinished()'), self.update_object)
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------
  
    def update_object(self):
        """ Handles the user changing the contents of the edit control.
        """
        try:
            self.value = unicode(self.control.text())
        except TraitError, excp:
            pass

#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyEditor ( Editor ):
    """ Base class for read-only style editors, which displays a read-only text
    field, containing a text representation of the object trait value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QLabel(self.str_value)
        self.set_tooltip()
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self.control.setText(self.str_value)

#-------------------------------------------------------------------------------
#  '_SimpleField' class:
#-------------------------------------------------------------------------------

class _SimpleField(QtGui.QLineEdit):

    def __init__(self, editor):
        QtGui.QLineEdit.__init__(self, editor.str_value)

        self.setReadOnly(True)
        self._editor = editor

    def mouseReleaseEvent(self, e):
        QtGui.QLineEdit.mouseReleaseEvent(self, e)

        if e.button() == QtCore.Qt.LeftButton:
            self._editor.popup_editor()
