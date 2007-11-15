#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various Boolean editors and the Boolean editor factory for the
PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

from enthought.traits.api    import Dict, Str, Any, true
from enthought.traits.ui.api import View
from editor              import Editor
from text_editor         import SimpleEditor         as TextEditor
from text_editor         import ToolkitEditorFactory as EditorFactory
from constants           import ReadonlyColor

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Mapping from user input text to Boolean values
mapping_trait = Dict( Str, Any, { 'True':  True,
                                  'true':  True,
                                  't':     True,
                                  'yes':   True,
                                  'y':     True,
                                  'False': False,
                                  'false': False,
                                  'f':     False,
                                  'no':    False,
                                  'n':     False,
                    } )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for Boolean editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Dictionary mapping user input to other values. 
    # These definitions override definitions in the 'text_editor' version
    mapping = mapping_trait  
    
    #---------------------------------------------------------------------------
    #  Traits view definition:  
    #---------------------------------------------------------------------------
    
    traits_view = View()    
    
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
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( Editor ):
    """ Simple style of editor for Boolean values, which displays a check box.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QCheckBox()
        self.control.connect(self.control, QtCore.SIGNAL('stateChanged(int)'),
                self.update_object)
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user clicking on the checkbox:
    #---------------------------------------------------------------------------
 
    def update_object ( self, state ):
        """ Handles the user clicking the checkbox.
        """
        self.value = bool(state)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        if self.value:
            self.control.setCheckState(QtCore.Qt.Checked)
        else:
            self.control.setCheckState(QtCore.Qt.Unchecked)
                                      
#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------
                               
class ReadonlyEditor ( Editor ):
    """ Read-only style of editor for Boolean values, which displays static text
    of either "True" or "False".
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QLineEdit()
        self.control.setReadOnly(True)

        pal = QtGui.QPalette(self.control.palette())
        pal.setColor(QtGui.QPalette.Base, ReadonlyColor)
        self.control.setPalette(pal)
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #
    #  (Should normally be overridden in a subclass)
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        if self.value:
            self.control.setText('True')
        else:
            self.control.setText('False')
