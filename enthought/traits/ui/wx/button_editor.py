#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: David C. Morrill
# Date: 10/21/2004
#
#  Symbols defined: ToolkitEditorFactory
#
#------------------------------------------------------------------------------
""" Defines the various button editors and the button editor factory for the
wxPython user interface toolkit.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import Str, Range, Enum, Property, Instance

from enthought.traits.trait_base \
    import user_name_for

from enthought.traits.ui.api \
    import View

from enthought.pyface.image_resource \
    import ImageResource

from editor_factory \
    import EditorFactory

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for buttons.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Value to set when the button is clicked
    value = Property

    # Optional label for the button
    label = Str

    # The name of the external object trait that the button label is synced to
    label_value = Str

    # (Optional) Image to display on the button
    image = Instance( ImageResource, allow_none = True )

    # Extra padding to add to both the left and the right sides
    width_padding = Range( 0, 31, 7 )

    # Extra padding to add to both the top and the bottom sides
    height_padding = Range( 0, 31, 5 )

    # Presentation style
    style = Enum( 'button', 'radio', 'toolbar', 'checkbox' )

    # Orientation of the text relative to the image
    orientation = Enum( 'vertical', 'horizontal' )

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
    label = Str

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        label = self.factory.label or user_name_for( self.name )
        self.control = wx.Button( parent, -1, label )
        self.sync_value( self.factory.label_value, 'label', 'from' )
        wx.EVT_BUTTON( parent, self.control.GetId(), self.update_object )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the 'label' trait being changed:
    #---------------------------------------------------------------------------

    def _label_changed ( self, label ):
        self.control.SetLabel( label )

    #---------------------------------------------------------------------------
    #  Handles the user clicking the button by setting the value on the object:
    #---------------------------------------------------------------------------

    def update_object ( self, event ):
        """ Handles the user clicking the button by setting the factory value
            on the object.
        """
        self.value = self.factory.value

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
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        from enthought.pyface.image_button import ImageButton

        factory       = self.factory
        self._control = ImageButton( parent,
                                     label          = factory.label,
                                     image          = factory.image,
                                     style          = factory.style,
                                     orientation    = factory.orientation,
                                     width_padding  = factory.width_padding,
                                     height_padding = factory.height_padding )
        self.control = self._control.control
        self._control.on_trait_change( self.update_object, 'clicked',
                                       dispatch = 'ui' )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( CustomEditor, self ).dispose()

        self._control.on_trait_change( self.update_object, 'clicked',
                                       remove = True )

