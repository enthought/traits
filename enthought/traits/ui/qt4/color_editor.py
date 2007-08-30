#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various color editors and the color editor factory, for the 
PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import true

from enthought.traits.ui.api \
    import View

from editor_factory \
    import EditorFactory, SimpleEditor, TextEditor, ReadonlyEditor

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Standard color samples:

color_choices = ( 0, 128, 192, 255 )
color_samples = [ None ] * 48
i             = 0
for r in color_choices:
    for g in color_choices:
        for b in ( 0, 128, 255 ):
            color_samples[i] = QtGui.QColor(r, g, b)
            i += 1  

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for color editors.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Is the underlying color trait mapped?
    mapped = true 
    
    #---------------------------------------------------------------------------
    #  Traits view definition:  
    #---------------------------------------------------------------------------
    
    traits_view = View( [ 'mapped{Is value mapped?}', '|[]>' ] )    
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------
    
    def simple_editor ( self, ui, object, name, description, parent ):
        return SimpleColorEditor( parent,
                                  factory     = self, 
                                  ui          = ui, 
                                  object      = object, 
                                  name        = name, 
                                  description = description ) 
    
    def custom_editor ( self, ui, object, name, description, parent ):
        return CustomColorEditor( parent,
                                  factory     = self, 
                                  ui          = ui, 
                                  object      = object, 
                                  name        = name, 
                                  description = description ) 
    
    def text_editor ( self, ui, object, name, description, parent ):
        return TextColorEditor( parent,
                                factory     = self, 
                                ui          = ui, 
                                object      = object, 
                                name        = name, 
                                description = description ) 
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        return ReadonlyColorEditor( parent,
                                    factory     = self, 
                                    ui          = ui, 
                                    object      = object, 
                                    name        = name, 
                                    description = description ) 
       
    #---------------------------------------------------------------------------
    #  Gets the PyQt color equivalent of the object trait:
    #---------------------------------------------------------------------------
    
    def to_pyqt_color ( self, editor ):
        """ Gets the PyQt color equivalent of the object trait.
        """
        if self.mapped:
            return getattr( editor.object, editor.name + '_' )

        return getattr( editor.object, editor.name )
 
    #---------------------------------------------------------------------------
    #  Gets the application equivalent of a PyQt value:
    #---------------------------------------------------------------------------
    
    def from_pyqt_color ( self, color ):
        """ Gets the application equivalent of a PyQt value.
        """
        return color
        
    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------
  
    def str_color ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        if isinstance(color, QtGui.QColor):
            return "(%d,%d,%d)" % (color.red(), color.green(), color.blue())

        return color
                                      
#-------------------------------------------------------------------------------
#  'SimpleColorEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleColorEditor ( SimpleEditor ):
    """ Simple style of color editor, which displays a text field whose 
    background color is the color value. Selecting the text field displays
    a dialog box for selecting a new color value.
    """
    
    #---------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #---------------------------------------------------------------------------
 
    def popup_editor(self):
        """ Invokes the pop-up editor for an object trait.
        """
        color = self.factory.to_pyqt_color(self)
        color = QtGui.QColorDialog.getColor(color, self.control)

        if color.isValid():
            self.value = self.factory.from_pyqt_color(color)
            self.update_editor()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        super( SimpleColorEditor, self ).update_editor()
        set_color( self )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------

    def string_value ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        return self.factory.str_color( color ) 

#-------------------------------------------------------------------------------
#  'CustomColorEditor' class:
#-------------------------------------------------------------------------------

class CustomColorEditor ( SimpleColorEditor ):
    """ Custom style of color editor, which displays a color editor panel.
    """
    
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = color_editor_for(self, parent)

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.control._swatch_editor.dispose()
        super( CustomColorEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        pass

    #---------------------------------------------------------------------------
    #  Updates the object trait when a color swatch is clicked:
    #---------------------------------------------------------------------------

    def update_object_from_swatch(self, control):
        """ Updates the object trait when a color swatch is clicked.
        """
        color = control.palette().color(QtGui.QPalette.Button)
        self.value = self.factory.from_pyqt_color(color)
        self.update_editor()

#-------------------------------------------------------------------------------
#  'TextColorEditor' class:
#-------------------------------------------------------------------------------

class TextColorEditor ( TextEditor ):
    """ Text style of color editor, which displays a text field whose 
    background color is the color value.
    """
    
    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------

    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        self.value = unicode(self.control.text())

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        super( TextColorEditor, self ).update_editor()
        set_color( self )

    #---------------------------------------------------------------------------
    #  Returns the text representation of a specified color value:
    #---------------------------------------------------------------------------

    def string_value ( self, color ):
        """ Returns the text representation of a specified color value.
        """
        return self.factory.str_color( color ) 

#-------------------------------------------------------------------------------
#  'ReadonlyColorEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyColorEditor ( ReadonlyEditor ):
    """ Read-only style of color editor, which displays a read-only text field
    whose background color is the color value.
    """
    
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QLineEdit(parent)
        self.control.setReadOnly(True)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        set_color( self )

#-------------------------------------------------------------------------------
#   Sets the color of the specified editor's color control: 
#-------------------------------------------------------------------------------

def set_color ( editor ):
    """  Sets the color of the specified color control.
    """
    color = editor.factory.to_pyqt_color(editor)
    pal = QtGui.QPalette(editor.control.palette())

    pal.setColor(QtGui.QPalette.Base, color)

    if (color.red() > 192 or color.blue() > 192 or color.green() > 192):
        pal.setColor(QtGui.QPalette.Text, QtCore.Qt.black)
    else:
        pal.setColor(QtGui.QPalette.Text, QtCore.Qt.white)

    editor.control.setPalette(pal)

#----------------------------------------------------------------------------
#  Creates a custom color editor panel for a specified editor:
#----------------------------------------------------------------------------

def color_editor_for(editor, parent):
    """ Creates a custom color editor panel for a specified editor.
    """
    # Create a panel to hold all of the buttons:
    panel = QtGui.QWidget(parent)

    layout = QtGui.QHBoxLayout(panel)
    layout.setMargin(0)

    panel._swatch_editor = swatch_editor = editor.factory.simple_editor( 
              editor.ui, editor.object, editor.name, editor.description, panel )
    swatch_editor.prepare( panel )
    control = swatch_editor.control
    layout.addWidget(control)

    # Add all of the color choice buttons:
    grid = QtGui.QGridLayout()
    grid.setMargin(0)
    grid.setSpacing(0)

    mapper = QtCore.QSignalMapper(panel)

    rows = 4
    cols = len(color_samples) / rows
    i = 0

    for r in range(rows):
        for c in range(cols):
            control = QtGui.QPushButton()
            control.setMaximumSize(18, 18)

            QtCore.QObject.connect(control, QtCore.SIGNAL('clicked()'),
                    mapper, QtCore.SLOT('map()'))
            mapper.setMapping(control, control)

            pal = QtGui.QPalette(control.palette())
            pal.setColor(QtGui.QPalette.Button, color_samples[i])
            control.setPalette(pal)

            grid.addWidget(control, r, c)
            editor.set_tooltip(control)

            i += 1

    QtCore.QObject.connect(mapper, QtCore.SIGNAL('mapped(QWidget *)'),
            editor.update_object_from_swatch)

    layout.addLayout(grid)

    # Return the panel as the result:
    return panel
