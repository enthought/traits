#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various text editors and the text editor factory, for the 
PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import Dict, Str, Any, Bool, TraitError
    
from enthought.traits.ui.api \
    import View, Group
    
from editor \
    import Editor
    
from editor_factory \
    import EditorFactory, ReadonlyEditor
    
from constants \
    import OKColor, ErrorColor

#-------------------------------------------------------------------------------
#  Define a simple identity mapping:
#-------------------------------------------------------------------------------

class _Identity ( object ):
    """ A simple indentity mapping.
    """
    def __call__ ( self, value ):    
        return value

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Mapping from user input text to other value
mapping_trait = Dict( Str, Any )

# Function used to evaluate textual user input
evaluate_trait = Any( _Identity() )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for text editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Dictionary that maps user input to other values
    mapping = mapping_trait
    
    # Is user input set on every keystroke?
    auto_set = Bool( True )
    
    # Is user input set when the Enter key is pressed?
    enter_set = Bool( False )
    
    # Is multi-line text allowed?
    multi_line = Bool( True )
    
    # Is user input unreadable? (e.g., for a password)
    password = Bool( False )
    
    # Function to evaluate textual user input
    evaluate = evaluate_trait
    
    # The object trait containing the function used to evaluate user input
    evaluate_name = Str
    
    #---------------------------------------------------------------------------
    #  Traits view definition:    
    #---------------------------------------------------------------------------
        
    traits_view = View( [ 'auto_set{Set value when text is typed}',
                          'enter_set{Set value when enter is pressed}',
                          'multi_line{Allow multiple lines of text}',
                          '<extras>',
                          '|options:[Options]>' ] )
    
    extras = Group( 'password{Is this a password field?}' )
    
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
        return CustomEditor( parent,
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
        return ReadonlyTextEditor( parent,
                                   factory     = self, 
                                   ui          = ui, 
                                   object      = object, 
                                   name        = name, 
                                   description = description ) 
                                      
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( Editor ):
    """ Simple style text editor, which displays a text field.
    """
    
    # Flag for window styles:
    base_style = QtGui.QLineEdit
    
    # Background color when input is OK:
    ok_color = OKColor

    #---------------------------------------------------------------------------
    #  Trait definitions: 
    #---------------------------------------------------------------------------
        
    # Function used to evaluate textual user input:
    evaluate = evaluate_trait
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        wtype = self.base_style
        self.evaluate = factory.evaluate
        self.sync_value(factory.evaluate_name, 'evaluate', 'from')

        if not factory.multi_line or factory.is_grid_cell or factory.password:
            wtype = QtGui.QLineEdit
        
        multi_line = (wtype is not QtGui.QLineEdit)
        if multi_line:
            self.scrollable = True

        control = wtype(self.str_value)

        # Create the palettes.
        self._error_palette = QtGui.QPalette(control.palette())
        self._error_palette.setColor(QtGui.QPalette.Base, ErrorColor)

        self._ok_palette = QtGui.QPalette(control.palette())
        self._ok_palette.setColor(QtGui.QPalette.Base, self.ok_color)

        control.setPalette(self._ok_palette)

        if factory.password:
            control.setEchoMode(QtGui.QLineEdit.Password)

        if factory.auto_set and not factory.is_grid_cell:
            QtCore.QObject.connect(control,
                    QtCore.SIGNAL('textEdited(QString)'), self.update_object)
        else:
            # Assume enter_set is set, otherwise the value will never get
            # updated.
            QtCore.QObject.connect(control, QtCore.SIGNAL('editingFinished()'),
                    self.update_object)

        self.control = control
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------
  
    def update_object ( self ):
        """ Handles the user entering input data in the edit control.
        """
        if not self._no_update and self.control is not None:
            try:
                self.value = self._get_user_value()
                self.control.setPalette(self._ok_palette)
                
                if self._error is not None:
                    self._error = None
                    self.ui.errors -= 1
                    
            except TraitError, excp:
                pass
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self._get_user_value() != self.value:
            self._no_update = True
            self.control.setText(self.str_value)
            self._no_update = False
            
        if self._error is not None:
            self._error = None
            self.ui.errors -= 1
            self.control.setPalette(self._ok_palette)

    #---------------------------------------------------------------------------
    #  Gets the actual value corresponding to what the user typed:
    #---------------------------------------------------------------------------
 
    def _get_user_value ( self ):
        """ Gets the actual value corresponding to what the user typed.
        """
        try:
            value = self.control.text()
        except AttributeError:
            value = self.control.toPlainText()

        value = unicode(value)

        try:
            value = self.evaluate( value )
        except:
            pass
            
        return self.factory.mapping.get( value, value )
        
    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------
        
    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        self.control.setPalette(self._error_palette)
        
        if self._error is None:
            self._error = True
            self.ui.errors += 1
        
#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor ( SimpleEditor ):
    """ Custom style of text editor, which displays a multi-line text field.
    """

    # FIXME: The wx version exposes a wx constant.
    # Flag for window style. This value overrides the default.
    base_style = QtGui.QTextEdit
                                     
#-------------------------------------------------------------------------------
#  'ReadonlyTextEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyTextEditor ( ReadonlyEditor ):
    """ Read-only style of text editor, which displays a read-only text field.
    """
    
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        new_value = self.str_value
        
        if self.factory.password:
            new_value = '*' * len(new_value)
            
        if self.item.resizable or self.item.height != -1:
            self.control.setPlainText(new_value)
        else:
            self.control.setText(new_value)
