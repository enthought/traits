#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various button editors and the button editor factory for the
PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import Str, Range, Enum, Property, Unicode

from enthought.traits.trait_base \
    import user_name_for

from enthought.traits.ui.api \
    import View

from enthought.traits.ui.ui_traits \
    import AView, Image

from editor_factory \
    import EditorFactory

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ PyQt editor factory for buttons.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Value to set when the button is clicked
    value = Property

    # Optional label for the button
    label = Unicode

    # The name of the external object trait that the button label is synced to
    label_value = Str

    # (Optional) Image to display on the button
    image = Image

    # Extra padding to add to both the left and the right sides
    width_padding = Range( 0, 31, 7 )

    # Extra padding to add to both the top and the bottom sides
    height_padding = Range( 0, 31, 5 )

    # Presentation style
    style = Enum( 'button', 'radio', 'toolbar', 'checkbox' )

    # Orientation of the text relative to the image
    orientation = Enum( 'vertical', 'horizontal' )

    # The optional view to display when the button is clicked:
    view = AView

    #---------------------------------------------------------------------------
    #  Traits view definition:
    #---------------------------------------------------------------------------

    traits_view = View( [ 'label', 'value', '|[]' ] )

    #---------------------------------------------------------------------------
    #  Implementation of the 'value' property:
    #---------------------------------------------------------------------------

    def _get_value ( self ):
        return self._value

    def _set_value ( self, value ):
        self._value = value
        if isinstance(value, basestring):
            try:
                self._value = int( value )
            except:
                try:
                    self._value = float( value )
                except:
                    pass

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, **traits ):
        self._value = 0
        super( ToolkitEditorFactory, self ).__init__( **traits )

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

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style editor for a button.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The button label
    label = Unicode

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        label = self.factory.label or self.item.get_label( self.ui )
        self.control = QtGui.QPushButton(label)
        self.sync_value( self.factory.label_value, 'label', 'from' )
        QtCore.QObject.connect(self.control, QtCore.SIGNAL('clicked()'),
                self.update_object )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the 'label' trait being changed:
    #---------------------------------------------------------------------------

    def _label_changed ( self, label ):
        self.control.setText(label)

    #---------------------------------------------------------------------------
    #  Handles the user clicking the button by setting the value on the object:
    #---------------------------------------------------------------------------

    def update_object (self):
        """ Handles the user clicking the button by setting the factory value
            on the object.
        """
        self.value = self.factory.value

        # If there is an associated view, then display it:
        if (self.factory is not None) and (self.factory.view is not None):
            self.object.edit_traits( view   = self.factory.view,
                                     parent = self.control )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style editor for a button, which can contain an image.
    """

    # The mapping of button styles to Qt classes.
    _STYLE_MAP = {
        'checkbox': QtGui.QCheckBox,
        'radio':    QtGui.QRadioButton,
        'toolbar':  QtGui.QToolButton
    }

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # FIXME: We ignore orientation, width_padding and height_padding.

        factory = self.factory

        btype = self._STYLE_MAP.get(factory.style, QtGui.QPushButton)
        self.control = btype()
        self.control.setText(factory.label)

        if factory.image is not None:
            self.control.setIcon(factory.image.create_icon())

        QtCore.QObject.connect(self.control, QtCore.SIGNAL('clicked()'),
                self.update_object )
        self.set_tooltip()
