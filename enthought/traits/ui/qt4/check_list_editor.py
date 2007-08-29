#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various editors and the editor factory for multi-selection
    enumerations, for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import logging

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import Range, List, Unicode, TraitError

from editor_factory \
    import EditorWithListFactory

from editor_factory \
    import TextEditor as BaseTextEditor

from editor \
    import EditorWithList
    
logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorWithListFactory ):
    """ PyQt editor factory for checklists.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Number of columns to use when the editor is displayed as a grid
    cols = Range( 1, 20 )

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
        return TextEditor( parent,
                           factory     = self,
                           ui          = ui,
                           object      = object,
                           name        = name,
                           description = description )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( EditorWithList ):
    """ Simple style of editor for checklists, which displays a combo box.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Checklist item names
    names = List( Unicode )

    # Checklist item values
    values = List

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.create_control( parent )
        super( SimpleEditor, self ).init( parent )

    #---------------------------------------------------------------------------
    #  Creates the initial editor control:
    #---------------------------------------------------------------------------

    def create_control ( self, parent ):
        """ Creates the initial editor control.
        """
        self.control = QtGui.QComboBox(parent)
        QtCore.QObject.connect(self.control,
                QtCore.SIGNAL('activated(QString)'), self.update_object)

    #---------------------------------------------------------------------------
    #  Handles the list of legal check list values being updated:
    #---------------------------------------------------------------------------

    def list_updated ( self, values ):
        """ Handles updates to the list of legal checklist values.
        """
        if (len( values ) > 0) and isinstance( values[0], basestring ):
           values = [ ( x, x.capitalize() ) for x in values ]
        self.values = valid_values = [ x[0] for x in values ]
        self.names  =                [ x[1] for x in values ]

        # Make sure the current value is still legal:
        modified  = False
        cur_value = parse_value( self.value )
        for i in range( len( cur_value ) - 1, -1, -1 ):
            if cur_value[i] not in valid_values:
                try:
                    del cur_value[i]
                    modified = True
                except TypeError, e:
                    logger.warn('Unable to remove non-current value [%s] from '
                        'values %s', cur_value[i], values)
        if modified:
            if isinstance( self.value, basestring ):
                cur_value = ','.join( cur_value )
            self.value = cur_value

        self.rebuild_editor()

    #---------------------------------------------------------------------------
    #  Rebuilds the editor after its definition is modified:
    #---------------------------------------------------------------------------

    def rebuild_editor ( self ):
        """ Rebuilds the editor after its definition is modified.
        """
        control = self.control
        control.clear()
        for name in self.names:
            control.addItem(name)
        self.update_editor()

    #----------------------------------------------------------------------------
    #  Handles the user selecting a new value from the combo box:
    #----------------------------------------------------------------------------

    def update_object ( self, text ):
        """ Handles the user selecting a new value from the combo box.
        """
        value = self.values[self.names.index(unicode(text))]
        if not isinstance(self.value, basestring):
           value = [value]
        self.value = value

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        try:
            self.control.setCurrentIndex(
                             self.values.index(parse_value(self.value)[0]))
        except:
            pass

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style of editor for checklists, which displays a set of check
        boxes.
    """
    
    #---------------------------------------------------------------------------
    #  Creates the initial editor control:
    #---------------------------------------------------------------------------

    def create_control ( self, parent ):
        """ Creates the initial editor control.
        """
        # Create a panel to hold all of the check boxes
        self.control = QtGui.QWidget(parent)

        layout = QtGui.QGridLayout(self.control)
        layout.setMargin(0)

        self._mapper = QtCore.QSignalMapper()
        QtCore.QObject.connect(self._mapper,
                QtCore.SIGNAL('mapped(QWidget *)'), self.update_object)

    #---------------------------------------------------------------------------
    #  Rebuilds the editor after its definition is modified:
    #---------------------------------------------------------------------------

    def rebuild_editor ( self ):
        """ Rebuilds the editor after its definition is modified.
        """
        control = self.control
        layout = control.layout()

        for cb in control.findChildren(QtGui.QCheckBox):
            cb.setParent(None)

        cur_value = parse_value( self.value )

        # Create a sizer to manage the radio buttons:
        labels = self.names
        values = self.values
        n      = len( labels )
        cols   = self.factory.cols
        rows   = (n + cols - 1) / cols
        incr   = [ n / cols ] * cols
        rem    = n % cols
        for i in range( cols ):
            incr[i] += (rem > i)
        incr[-1] = -(reduce( lambda x, y: x + y, incr[:-1], 0 ) - 1)

        # Add the set of all possible choices:
        index = 0
        for i in range( rows ):
            for j in range( cols ):
                if n > 0:
                    cb = QtGui.QCheckBox(labels[index], control)
                    cb.value = values[index]

                    if cb.value in cur_value:
                        cb.setCheckState(QtCore.Qt.Checked)
                    else:
                        cb.setCheckState(QtCore.Qt.Unchecked)

                    QtCore.QObject.connect(cb, QtCore.SIGNAL('clicked()'),
                            self._mapper, QtCore.SLOT('map()'))
                    self._mapper.setMapping(cb, cb)

                    layout.addWidget(cb, i, j)

                    index += incr[j]
                    n -= 1

    #---------------------------------------------------------------------------
    #  Handles the user clicking one of the 'custom' check boxes:
    #---------------------------------------------------------------------------

    def update_object(self, cb):
        """ Handles the user clicking one of the custom check boxes.
        """
        cur_value = parse_value(self.value)
        if cb.checkState() == QtCore.Qt.Checked:
            cur_value.append(cb.value)
        else:
            cur_value.remove(cb.value)

        if isinstance(self.value, basestring):
            cur_value = ','.join(cur_value)

        self.value = cur_value

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        new_values = parse_value( self.value )
        for cb in self.control.findChildren(QtGui.QCheckBox):
            if cb.value in new_values:
                cb.setCheckState(QtCore.Qt.Checked)
            else:
                cb.setCheckState(QtCore.Qt.Unchecked)

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor ( BaseTextEditor ):
    """ Text style of editor for checklists, which displays a text field.
    """
    
    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------

    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        try:
            value = unicode(self.control.text())
            value = eval( value )
        except:
            pass
        try:
            self.value = value
        except TraitError, excp:
            pass

#-------------------------------------------------------------------------------
#  Parse a value into a list:
#-------------------------------------------------------------------------------

def parse_value ( value ):
    """ Parses a value into a list.
    """
    if value is None:
       return []
    if type( value ) is not str:
       return value[:]
    return [ x.strip() for x in value.split( ',' ) ]
