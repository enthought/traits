#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various editors and the editor factory for single-selection 
    enumerations, for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

from string \
    import ascii_lowercase
    
from editor \
    import Editor
    
from constants \
    import OKColor, ErrorColor
    
from helper \
    import enum_values_changed
    
from editor_factory \
    import EditorFactory
    
from enthought.traits.api \
    import Any, Range, Enum, Str, Trait, Event, Property, Bool
           
from enthought.traits.ui.ui_traits \
    import SequenceTypes

#-------------------------------------------------------------------------------
#  Trait definitions:  
#-------------------------------------------------------------------------------

# Supported display modes for a custom style editor
Mode = Enum( 'radio', 'list' )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for enumeration editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------
    
    # Values to enumerate (can be a list, tuple, dict, or a CTrait or 
    # TraitHandler that is "mapped"):
    values = Any    
                              
    # Extended name of the trait on **object** containing the enumeration data:
    name = Str
                              
    # (Optional) Function used to evaluate text input:
    evaluate = Any 

    # Is user input set on every keystroke (when text input is allowed)?
    auto_set = Bool( True )
    
    # Number of columns to use when displayed as a grid:
    cols = Range( 1, 20 ) 
    
    # Display modes supported for a custom style editor:
    mode = Mode           
    
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
        if self.mode == 'radio':
            return RadioEditor( parent,
                                factory     = self, 
                                ui          = ui, 
                                object      = object, 
                                name        = name, 
                                description = description )
        else:
            return ListEditor( parent,
                               factory     = self, 
                               ui          = ui, 
                               object      = object, 
                               name        = name, 
                               description = description ) 
                                      
#-------------------------------------------------------------------------------
#  'BaseEditor' class:
#-------------------------------------------------------------------------------
                               
class BaseEditor ( Editor ):
    """ Base class for enumeration editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Current set of enumeration names:
    names = Property
    
    # Current mapping from names to values:
    mapping = Property
    
    # Current inverse mapping from values to names:
    inverse_mapping = Property  
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if factory.name != '':
            self._object, self._name, self._value = \
                self.parse_extended_name( factory.name )
            self.values_changed()
            self._object.on_trait_change( self._values_changed, 
                                          ' ' + self._name, dispatch = 'ui' )
        else:
            factory.on_trait_change( self.rebuild_editor, 'values_modified', 
                                     dispatch = 'ui' )
            
    #---------------------------------------------------------------------------
    #  Gets the current set of enumeration names:  
    #---------------------------------------------------------------------------
    
    def _get_names ( self ):
        """ Gets the current set of enumeration names.
        """
        if self._object is None:
            return self.factory._names
            
        return self._names
            
    #---------------------------------------------------------------------------
    #  Gets the current mapping:
    #---------------------------------------------------------------------------
    
    def _get_mapping ( self ):
        """ Gets the current mapping.
        """
        if self._object is None:
            return self.factory._mapping
            
        return self._mapping
            
    #---------------------------------------------------------------------------
    #  Gets the current inverse mapping:
    #---------------------------------------------------------------------------
    
    def _get_inverse_mapping ( self ):
        """ Gets the current inverse mapping.
        """
        if self._object is None:
            return self.factory._inverse_mapping
            
        return self._inverse_mapping
            
    #---------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory 
    #  object's 'values' trait changes:  
    #---------------------------------------------------------------------------
                        
    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Recomputes the cached data based on the underlying enumeration model:
    #---------------------------------------------------------------------------
                        
    def values_changed ( self ):
        """ Recomputes the cached data based on the underlying enumeration model.
        """
        self._names, self._mapping, self._inverse_mapping = \
            enum_values_changed( self._value() )
            
    #---------------------------------------------------------------------------
    #  Handles the underlying object model's enumeration set being changed:  
    #---------------------------------------------------------------------------
                        
    def _values_changed ( self ):
        """ Handles the underlying object model's enumeration set being changed.
        """
        self.values_changed()
        self.rebuild_editor()
        
    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( BaseEditor, self ).dispose()
        
        if self._object is not None:
            self._object.on_trait_change( self._values_changed, 
                                          ' ' + self._name, remove = True )
        else:
            self.factory.on_trait_change( self.rebuild_editor,
                                          'values_modified', remove = True )
                                      
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( BaseEditor ):
    """ Simple style of enumeration editor, which displays a combo box.
    """
    
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( SimpleEditor, self ).init( parent )
        
        self.control = control = QtGui.QComboBox(parent)
        control.addItems(self.names)
        QtCore.QObject.connect(control,
                QtCore.SIGNAL('currentIndexChanged(QString)'),
                self.update_object)

        if self.factory.evaluate is not None:
            control.setEditable(True)
            QtCore.QObject.connect(control,
                    QtCore.SIGNAL('editTextChanged(QString)'),
                    self.update_text_object)

        self._no_enum_update = 0

    #---------------------------------------------------------------------------
    #  Handles the user selecting a new value from the combo box:
    #---------------------------------------------------------------------------
  
    def update_object (self, text):
        """ Handles the user selecting a new value from the combo box.
        """
        self._no_enum_update += 1
        try:
            self.value = self.mapping[unicode(text)]
        except:
            pass
        self._no_enum_update -= 1

    #---------------------------------------------------------------------------
    #  Handles the user typing text into the combo box text entry field:
    #---------------------------------------------------------------------------
    
    def update_text_object(self, text):
        """ Handles the user typing text into the combo box text entry field.
        """
        if self._no_enum_update == 0:
            value = unicode(text)
            try:
                value = self.mapping[value]
            except:
                try:
                    value = self.factory.evaluate(value)
                except Exception, excp:
                    self.error( excp )
                    return

            self._no_enum_update += 1
            self.value = value
            self._set_background(OKColor)
            self._no_enum_update -= 1
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        if self._no_enum_update == 0:
            if self.factory.evaluate is None:
                try:
                    idx = self.control.findText(self.inverse_mapping[self.value])
                    self.control.setCurrentIndex(idx)
                except:
                    pass
            else:
                try:
                    self.control.setEditText(self.str_value)
                except:
                    pass
        
    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------
        
    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        self._set_background(ErrorColor)
        
    #---------------------------------------------------------------------------
    #  Sets the background color of the QLineEdit of the QComboBox.
    #---------------------------------------------------------------------------
        
    def _set_background(self, col):
        le = self.control.lineEdit()
        pal = QtGui.QPalette(le.palette())
        pal.setColor(QtGui.QPalette.Base, col)
        le.setPalette(pal)

    #---------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory 
    #  object's 'values' trait changes:  
    #---------------------------------------------------------------------------
                        
    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """
        self.control.clear()
        self.control.addItems(self.names)

        self.update_editor()
                                      
#-------------------------------------------------------------------------------
#  'RadioEditor' class:
#-------------------------------------------------------------------------------
                               
class RadioEditor ( BaseEditor ):
    """ Enumeration editor, used for the "custom" style, that displays radio
    buttons.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( RadioEditor, self ).init( parent )
            
        # Create a panel to hold all of the radio buttons:
        self.control = QtGui.QWidget(parent)

        layout = QtGui.QGridLayout(self.control)
        layout.setMargin(0)

        self._mapper = QtCore.QSignalMapper()
        QtCore.QObject.connect(self._mapper,
                QtCore.SIGNAL('mapped(QWidget *)'), self.update_object)

        self.rebuild_editor()
   
    #---------------------------------------------------------------------------
    #  Handles the user clicking one of the 'custom' radio buttons:
    #---------------------------------------------------------------------------
    
    def update_object(self, rb):
        """ Handles the user clicking one of the custom radio buttons.
        """
        try:
            self.value = rb.value
        except:
            pass
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        value = self.value
        for rb in self.control.findChildren(QtGui.QRadioButton):
            rb.setChecked(rb.value == value)

    #---------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory 
    #  object's 'values' trait changes:  
    #---------------------------------------------------------------------------
                        
    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """
        # Clear any existing content:
        for rb in self.control.findChildren(QtGui.QRadioButton):
            rb.setParent(None)

        # Get the current trait value:
        cur_name = self.str_value
                           
        # Create a sizer to manage the radio buttons:
        names   = self.names
        mapping = self.mapping
        n       = len( names )
        cols    = self.factory.cols
        rows    = (n + cols - 1) / cols
        incr    = [ n / cols ] * cols
        rem     = n % cols
        for i in range( cols ):
            incr[i] += (rem > i)
        incr[-1] = -(reduce( lambda x, y: x + y, incr[:-1], 0 ) - 1)

        # Add the set of all possible choices:
        layout = self.control.layout()
        index = 0

        for i in range( rows ):
            for j in range( cols ):
                if n > 0:
                    name = label = names[ index ]
                    if label[:1] in ascii_lowercase:
                        label = label.capitalize()
                    rb = QtGui.QRadioButton(label)
                    rb.value = mapping[name]

                    rb.setChecked(name == cur_name)

                    QtCore.QObject.connect(rb, QtCore.SIGNAL('clicked()'),
                            self._mapper, QtCore.SLOT('map()'))
                    self._mapper.setMapping(rb, rb)

                    self.set_tooltip(rb)
                    layout.addWidget(rb, i, j)

                    index += incr[j]
                    n -= 1

#-------------------------------------------------------------------------------
#  'ListEditor' class:
#-------------------------------------------------------------------------------
                               
class ListEditor ( BaseEditor ):
    """ Enumeration editor, used for the "custom" style, that displays a list
    box.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( ListEditor, self ).init( parent )
        
        self.control = QtGui.QListWidget(parent)
        QtCore.QObject.connect(self.control,
                QtCore.SIGNAL('currentTextChanged(QString)'),
                self.update_object)

        self.rebuild_editor()
   
    #---------------------------------------------------------------------------
    #  Handles the user selecting a list box item:
    #---------------------------------------------------------------------------
    
    def update_object(self, text):
        """ Handles the user selecting a list box item.
        """
        value = unicode(text)
        try:
            value = self.mapping[ value ]
        except:
            try:
                value = self.factory.evaluate( value )
            except:
                pass
        try:
            self.value = value
        except:
            pass
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        control = self.control
        try:
            value = self.inverse_mapping[self.value]

            for row in range(control.count()):
                itm = control.item(row)

                if itm.text() == value:
                    control.setCurrentItem(itm)
                    control.scrollToItem(itm)
                    break
        except:
            pass
            
    #---------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory 
    #  object's 'values' trait changes:  
    #---------------------------------------------------------------------------
                        
    def rebuild_editor ( self ):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """
        self.control.clear()

        for name in self.names:
            self.control.addItem(name)
