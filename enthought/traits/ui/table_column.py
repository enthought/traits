#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   07/01/2005
#
#------------------------------------------------------------------------------

""" Defines the table column descriptor used by the editor and editor factory
    classes for numeric and table editors.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..api import (Any, Bool, Callable, Color, Constant, Enum, Expression, Float,
    Font, HasPrivateTraits, Instance, Int, Property, Str)

from ..trait_base import user_name_for, xgetattr

from .editor_factory import EditorFactory
from .menu import Menu
from .ui_traits import Image, AView, EditorStyle
from .view import View

# Set up a logger:
import logging
logger = logging.getLogger( __name__ )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Flag used to indicate user has not specified a column label
UndefinedLabel = '???'

#-------------------------------------------------------------------------------
#  'TableColumn' class:
#-------------------------------------------------------------------------------

class TableColumn ( HasPrivateTraits ):
    """ Represents a column in a table editor.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Column label to use for this column:
    label = Str( UndefinedLabel )

    # Type of data contained by the column:
    type = Enum( 'text' )

    # Text color for this column:
    text_color = Color( 'black' )

    # Text font for this column:
    text_font = Font

    # Cell background color for this column:
    cell_color = Color( 'white' )

    # Cell background color for non-editable columns:
    read_only_cell_color = Color( 0xF4F3EE )

    # Cell graph color:
    graph_color = Color( 0xDDD9CC )

    # Horizontal alignment of text in the column:
    horizontal_alignment = Enum( 'left', [ 'left', 'center', 'right' ] )

    # Vertical alignment of text in the column:
    vertical_alignment = Enum( 'center', [ 'top', 'center', 'bottom' ] )

    # The image to display in the cell:
    image = Image

    # Renderer used to render the contents of this column:
    renderer = Any # A toolkit specific renderer

    # Is the table column visible (i.e., viewable)?
    visible = Bool( True )

    # Is this column editable?
    editable = Bool( True )

    # Is the column automatically edited/viewed (i.e. should the column editor
    # or popup be activated automatically on mouse over)?
    auto_editable = Bool( False )

    # Can external objects be dropped on the column?
    droppable = Bool( False )

    # Context menu to display when this column is right-clicked:
    menu = Instance( Menu )

    # The tooltip to display when the mouse is over the column:
    tooltip = Str

    # The width of the column (< 0.0: Default, 0.0..1.0: fraction of total table
    # width, > 1.0: absolute width in pixels):
    width = Float( -1.0 )

    # The width of the column while it is being edited (< 0.0: Default,
    # 0.0..1.0: fraction of total table width, > 1.0: absolute width in pixels):
    edit_width = Float( -1.0 )

    # The height of the column cell's row while it is being edited
    # (< 0.0: Default, 0.0..1.0: fraction of total table height,
    # > 1.0: absolute height in pixels):
    edit_height = Float( -1.0 )

    # The view (if any) to display when clicking a non-editable cell:
    view = AView

    # Optional maximum value a numeric cell value can have:
    maximum = Float( trait_value = True )

    #---------------------------------------------------------------------------
    #  Returns the actual object being edited:
    #---------------------------------------------------------------------------

    def get_object ( self, object ):
        """ Returns the actual object being edited.
        """
        return object

    #---------------------------------------------------------------------------
    #  Gets the label of the column:
    #---------------------------------------------------------------------------

    def get_label ( self ):
        """ Gets the label of the column.
        """
        return self.label

    #---------------------------------------------------------------------------
    #  Returns the width of the column:
    #---------------------------------------------------------------------------

    def get_width ( self ):
        """ Returns the width of the column.
        """
        return self.width

    #---------------------------------------------------------------------------
    #  Returns the edit width of the column:
    #---------------------------------------------------------------------------

    def get_edit_width ( self, object ):
        """ Returns the edit width of the column.
        """
        return self.edit_width

    #---------------------------------------------------------------------------
    #  Returns the height of the column cell's row while it is being edited:
    #---------------------------------------------------------------------------

    def get_edit_height ( self, object ):
        """ Returns the height of the column cell's row while it is being
            edited.
        """
        return self.edit_height

    #---------------------------------------------------------------------------
    #  Gets the type of data for the column for a specified object:
    #---------------------------------------------------------------------------

    def get_type ( self, object ):
        """ Gets the type of data for the column for a specified object.
        """
        return self.type

    #---------------------------------------------------------------------------
    #  Returns the text color for the column for a specified object:
    #---------------------------------------------------------------------------

    def get_text_color ( self, object ):
        """ Returns the text color for the column for a specified object.
        """
        return self.text_color_

    #---------------------------------------------------------------------------
    #  Returns the text font for the column for a specified object:
    #---------------------------------------------------------------------------

    def get_text_font ( self, object ):
        """ Returns the text font for the column for a specified object.
        """
        return self.text_font

    #---------------------------------------------------------------------------
    #  Returns the cell background color for the column for a specified object:
    #---------------------------------------------------------------------------

    def get_cell_color ( self, object ):
        """ Returns the cell background color for the column for a specified
            object.
        """
        if self.is_editable( object ):
            return self.cell_color_
        return self.read_only_cell_color_

    #---------------------------------------------------------------------------
    #  Returns the cell background graph color for the column for a specified
    #  object:
    #---------------------------------------------------------------------------

    def get_graph_color ( self, object ):
        """ Returns the cell background graph color for the column for a
            specified object.
        """
        return self.graph_color_

    #---------------------------------------------------------------------------
    #  Returns the horizontal alignment for the column for a specified object:
    #---------------------------------------------------------------------------

    def get_horizontal_alignment ( self, object ):
        """ Returns the horizontal alignment for the column for a specified
            object.
        """
        return self.horizontal_alignment

    #---------------------------------------------------------------------------
    #  Returns the vertical alignment for the column for a specified object:
    #---------------------------------------------------------------------------

    def get_vertical_alignment ( self, object ):
        """ Returns the vertical alignment for the column for a specified
            object.
        """
        return self.vertical_alignment

    #---------------------------------------------------------------------------
    #  Returns the image to display for the column for a specified object:
    #---------------------------------------------------------------------------

    def get_image ( self, object ):
        """ Returns the image to display for the column for a specified object.
        """
        return self.image

    #---------------------------------------------------------------------------
    #  Returns the renderer for the column of a specified object:
    #---------------------------------------------------------------------------

    def get_renderer ( self, object ):
        """ Returns the renderer for the column of a specified object.
        """
        return self.renderer

    #---------------------------------------------------------------------------
    #  Returns whether the column is editable for a specified object:
    #---------------------------------------------------------------------------

    def is_editable ( self, object ):
        """ Returns whether the column is editable for a specified object.
        """
        return self.editable

    #---------------------------------------------------------------------------
    #  Returns whether the column is autoamtically edited/viewed for a specified
    #  object:
    #---------------------------------------------------------------------------

    def is_auto_editable ( self, object ):
        """ Returns whether the column is automatically edited/viewed for a
            specified object.
        """
        return self.auto_editable

    #---------------------------------------------------------------------------
    #  Returns whether a specified value is valid for dropping on the column
    #  for a specified object:
    #---------------------------------------------------------------------------

    def is_droppable ( self, object, value ):
        """ Returns whether a specified value is valid for dropping on the
            column for a specified object.
        """
        return self.droppable

    #---------------------------------------------------------------------------
    #  Returns the context menu to display when the user right-clicks on the
    #  column for a specified object:
    #---------------------------------------------------------------------------

    def get_menu ( self, object ):
        """ Returns the context menu to display when the user right-clicks on
            the column for a specified object.
        """
        return self.menu

    #---------------------------------------------------------------------------
    #  Returns the tooltip to display when the user mouses over the column for
    #  a specified object:
    #---------------------------------------------------------------------------

    def get_tooltip ( self, object ):
        """ Returns the tooltip to display when the user mouses over the column
            for a specified object.
        """
        return self.tooltip

    #---------------------------------------------------------------------------
    #  Returns the view to display when clicking a non-editable cell:
    #---------------------------------------------------------------------------

    def get_view ( self, object ):
        """ Returns the view to display when clicking a non-editable cell.
        """
        return self.view

    #---------------------------------------------------------------------------
    #  Returns the maximum value a numeric column can have:
    #---------------------------------------------------------------------------

    def get_maximum ( self, object ):
        """ Returns the maximum value a numeric column can have.
        """
        return self.maximum

    #---------------------------------------------------------------------------
    #  Called when the user clicks on the column:
    #---------------------------------------------------------------------------

    def on_click ( self, object ):
        """ Called when the user clicks on the column.
        """
        pass

    #---------------------------------------------------------------------------
    #  Called when the user double-clicks on the column:
    #---------------------------------------------------------------------------

    def on_dclick ( self, object ):
        """ Called when the user clicks on the column.
        """
        pass

    #---------------------------------------------------------------------------
    #  Returns the string representation of the table column:
    #---------------------------------------------------------------------------

    def __str__ ( self ):
        """ Returns the string representation of the table column.
        """
        return self.get_label()

#-------------------------------------------------------------------------------
#  'ObjectColumn' class:
#-------------------------------------------------------------------------------

class ObjectColumn ( TableColumn ):
    """ A column for editing objects.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Name of the object trait associated with this column:
    name = Str

    # Column label to use for this column:
    label = Property

    # Trait editor used to edit the contents of this column:
    editor = Instance( EditorFactory )

    # The editor style to use to edit the contents of this column:
    style = EditorStyle

    # Format string to apply to column values:
    format = Str( '%s' )

    # Format function to apply to column values:
    format_func = Callable

    #---------------------------------------------------------------------------
    #  Trait view definitions:
    #---------------------------------------------------------------------------

    traits_view = View( [ [ 'name', 'label', 'type',
                            '|[Column Information]' ],
                          [ 'horizontal_alignment{Horizontal}@',
                            'vertical_alignment{Vertical}@',
                            '|[Alignment]' ],
                          [ 'editable', '9', 'droppable', '9', 'visible',
                            '-[Options]>' ],
                          '|{Column}' ],
                        [ [ 'text_color@', 'cell_color@',
                            'read_only_cell_color@',
                            '|[UI Colors]' ],
                          '|{Colors}' ],
                        [ [ 'text_font@',
                            '|[Font]<>' ],
                          '|{Font}' ],
                        [ 'menu@',
                          '|{Menu}' ],
                        [ 'editor@',
                          '|{Editor}' ] )

    #---------------------------------------------------------------------------
    #  Implementation of the 'label' property:
    #---------------------------------------------------------------------------

    def _get_label ( self ):
        """ Gets the label of the column.
        """
        if self._label is not None:
            return self._label
        return user_name_for( self.name )

    def _set_label ( self, label ):
        old, self._label = self._label, label
        if old != label:
            self.trait_property_changed( 'label', old, label )

    #---------------------------------------------------------------------------
    #  Gets the value of the column for a specified object:
    #---------------------------------------------------------------------------

    def get_raw_value ( self, object ):
        """ Gets the unformatted value of the column for a specified object.
        """
        try:
            return xgetattr( self.get_object( object ), self.name )
        except:
            return None

    def get_value ( self, object ):
        """ Gets the formatted value of the column for a specified object.
        """
        try:
            if self.format_func is not None:
                return self.format_func( self.get_raw_value( object ) )

            return self.format % ( self.get_raw_value( object ), )
        except:
            logger.exception( 'Error occurred trying to format a %s value' %
                              self.__class__.__name__ )
            return 'Format!'

    #---------------------------------------------------------------------------
    #  Returns the drag value for the column:
    #---------------------------------------------------------------------------

    def get_drag_value ( self, object ):
        """Returns the drag value for the column.
        """
        return self.get_raw_value( object )

    #---------------------------------------------------------------------------
    #  Sets the value of the column for a specified object:
    #---------------------------------------------------------------------------

    def set_value ( self, object, value ):
        """ Sets the value of the column for a specified object.
        """
        target, name = self.target_name( object )
        setattr( target, name, value )

    #---------------------------------------------------------------------------
    #  Gets the editor for the column of a specified object:
    #---------------------------------------------------------------------------

    def get_editor ( self, object ):
        """ Gets the editor for the column of a specified object.
        """
        if self.editor is not None:
            return self.editor

        target, name = self.target_name( object )

        return target.base_trait( name ).get_editor()

    #---------------------------------------------------------------------------
    #  Gets the editor style for the column of a specified object:
    #---------------------------------------------------------------------------

    def get_style ( self, object ):
        """ Gets the editor style for the column of a specified object.
        """
        return self.style

    #---------------------------------------------------------------------------
    #  Returns the result of comparing the column of two different objects:
    #---------------------------------------------------------------------------

    def cmp ( self, object1, object2 ):
        """ Returns the result of comparing the column of two different objects.
        """
        return cmp( self.get_raw_value( object1 ),
                    self.get_raw_value( object2 ) )

    #---------------------------------------------------------------------------
    #  Returns whether a specified value is valid for dropping on the column
    #  for a specified object:
    #---------------------------------------------------------------------------

    def is_droppable ( self, object, value ):
        """ Returns whether a specified value is valid for dropping on the
            column for a specified object.
        """
        if self.droppable:
            try:
                target, name = self.target_name( object )
                target.base_trait( name ).validate( target, name, value )
                return True
            except:
                pass

        return False

    #---------------------------------------------------------------------------
    #  Returns the target object and name for the column:
    #---------------------------------------------------------------------------

    def target_name ( self, object ):
        """ Returns the target object and name for the column.
        """
        object = self.get_object( object )
        name   = self.name
        col    = name.rfind( '.' )
        if col < 0:
            return ( object, name )

        return ( xgetattr( object, name[ :col ] ), name[ col + 1: ] )

#-------------------------------------------------------------------------------
#  'ExpressionColumn' class:
#-------------------------------------------------------------------------------

class ExpressionColumn ( ObjectColumn ):
    """ A column for displaying computed values.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The Python expression used to return the value of the column:
    expression = Expression

    # Is this column editable?
    editable = Constant( False )

    # The globals dictionary that should be passed to the expression evaluation:
    globals = Any( {} )

    #---------------------------------------------------------------------------
    #  Gets the value of the column for a specified object:
    #---------------------------------------------------------------------------

    def get_raw_value ( self, object ):
        """ Gets the unformatted value of the column for a specified object.
        """
        try:
            return eval( self.expression_, self.globals, { 'object': object } )
        except:
            logger.exception( 'Error evaluating table column expression: %s' %
                              self.expression )
            return None

#-------------------------------------------------------------------------------
#  'NumericColumn' class:
#-------------------------------------------------------------------------------

class NumericColumn ( ObjectColumn ):
    """ A column for editing Numeric arrays.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Column label to use for this column
    label = Property

    # Text color this column when selected
    selected_text_color = Color( 'black' )

    # Text font for this column when selected
    selected_text_font = Font

    # Cell background color for this column when selected
    selected_cell_color = Color( 0xD8FFD8 )

    # Formatting string for the cell value
    format = Str( '%s' )

    # Horizontal alignment of text in the column; this value overrides the
    # default.
    horizontal_alignment = 'center'

    #---------------------------------------------------------------------------
    #  Implementation of the 'label' property:
    #---------------------------------------------------------------------------

    def _get_label ( self ):
        """ Gets the label of the column.
        """
        if self._label is not None:
            return self._label
        return self.name

    def _set_label ( self, label ):
        old, self._label = self._label, label
        if old != label:
            self.trait_property_changed( 'label', old, label )

    #---------------------------------------------------------------------------
    #  Gets the type of data for the column for a specified object row:
    #---------------------------------------------------------------------------

    def get_type ( self, object ):
        """ Gets the type of data for the column for a specified object row.
        """
        return self.type

    #---------------------------------------------------------------------------
    #  Returns the text color for the column for a specified object row:
    #---------------------------------------------------------------------------

    def get_text_color ( self, object ):
        """ Returns the text color for the column for a specified object row.
        """
        if self._is_selected( object ):
            return self.selected_text_color_
        return self.text_color_

    #---------------------------------------------------------------------------
    #  Returns the text font for the column for a specified object row:
    #---------------------------------------------------------------------------

    def get_text_font ( self, object ):
        """ Returns the text font for the column for a specified object row.
        """
        if self._is_selected( object ):
            return self.selected_text_font
        return self.text_font

    #---------------------------------------------------------------------------
    #  Returns the cell background color for the column for a specified object
    #  row:
    #---------------------------------------------------------------------------

    def get_cell_color ( self, object ):
        """ Returns the cell background color for the column for a specified
            object row.
        """
        if self.is_editable( object ):
            if self._is_selected( object ):
                return self.selected_cell_color_
            return self.cell_color_
        return self.read_only_cell_color_

    #---------------------------------------------------------------------------
    #  Returns the horizontal alignment for the column for a specified object
    #  row:
    #---------------------------------------------------------------------------

    def get_horizontal_alignment ( self, object ):
        """ Returns the horizontal alignment for the column for a specified
            object row.
        """
        return self.horizontal_alignment

    #---------------------------------------------------------------------------
    #  Returns the vertical alignment for the column for a specified object row:
    #---------------------------------------------------------------------------

    def get_vertical_alignment ( self, object ):
        """ Returns the vertical alignment for the column for a specified
            object row.
        """
        return self.vertical_alignment

    #---------------------------------------------------------------------------
    #  Returns whether the column is editable for a specified object row:
    #---------------------------------------------------------------------------

    def is_editable ( self, object ):
        """ Returns whether the column is editable for a specified object row.
        """
        return self.editable

    #---------------------------------------------------------------------------
    #  Returns whether a specified value is valid for dropping on the column
    #  for a specified object row:
    #---------------------------------------------------------------------------

    def is_droppable ( self, object, row, value ):
        """ Returns whether a specified value is valid for dropping on the
            column for a specified object row.
        """
        return self.droppable

    #---------------------------------------------------------------------------
    #  Returns the context menu to display when the user right-clicks on the
    #  column for a specified object row:
    #---------------------------------------------------------------------------

    def get_menu ( self, object, row ):
        """ Returns the context menu to display when the user right-clicks on
            the column for a specified object row.
        """
        return self.menu

    #---------------------------------------------------------------------------
    #  Gets the value of the column for a specified object row:
    #---------------------------------------------------------------------------

    def get_value ( self, object ):
        """ Gets the value of the column for a specified object row.
        """
        try:
            value = getattr( object, self.name )
            try:
                return self.format % ( value, )
            except:
                return 'Format!'
        except:
            return 'Undefined!'

    #---------------------------------------------------------------------------
    #  Sets the value of the column for a specified object row:
    #---------------------------------------------------------------------------

    def set_value ( self, object, row, value ):
        """ Sets the value of the column for a specified object row.
        """
        column = self.get_data_column( object )
        column[ row ] = type( column[ row ] )( value )

    #---------------------------------------------------------------------------
    #  Gets the editor for the column of a specified object row:
    #---------------------------------------------------------------------------

    def get_editor ( self, object ):
        """ Gets the editor for the column of a specified object row.
        """
        return super( NumericColumn, self ).get_editor( object )

    #---------------------------------------------------------------------------
    #  Gets the entire contents of the specified object column:
    #---------------------------------------------------------------------------

    def get_data_column ( self, object ):
        """ Gets the entire contents of the specified object column.
        """
        return getattr( object, self.name )

    #---------------------------------------------------------------------------
    #  Returns whether a specified object row is selected or not:
    #---------------------------------------------------------------------------

    def _is_selected ( self, object ):
        """ Returns whether a specified object row is selected.
        """
        if hasattr(object, 'model_selection') \
                and object.model_selection is not None:
            return True
        return False

#-------------------------------------------------------------------------------
#  'ListColumn' class:
#-------------------------------------------------------------------------------

class ListColumn ( TableColumn ):
    """ A column for editing lists.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    #Label to use for this column
    label = Property

    # Index of the list element associated with this column
    index = Int

    # Is this column editable? This value overrides the base class default.
    editable = False

    #---------------------------------------------------------------------------
    #  Trait view definitions:
    #---------------------------------------------------------------------------

    traits_view = View( [ [ 'index', 'label', 'type', '|[Column Information]' ],
                          [ 'text_color@', 'cell_color@', '|[UI Colors]' ] ] )

    #---------------------------------------------------------------------------
    #  Implementation of the 'label' property:
    #---------------------------------------------------------------------------

    def _get_label ( self ):
        """ Gets the label of the column.
        """
        if self._label is not None:
            return self._label
        return 'Column %d' % (self.index + 1)

    def _set_label ( self, label ):
        old, self._label = self._label, label
        if old != label:
            self.trait_property_changed( 'label', old, label )

    #---------------------------------------------------------------------------
    #  Gets the value of the column for a specified object:
    #---------------------------------------------------------------------------

    def get_value ( self, object ):
        """ Gets the value of the column for a specified object.
        """
        return unicode( object[ self.index ] )

    #---------------------------------------------------------------------------
    #  Sets the value of the column for a specified object:
    #---------------------------------------------------------------------------

    def set_value ( self, object, value ):
        """ Sets the value of the column for a specified object.
        """
        object[ self.index ] = value

    #---------------------------------------------------------------------------
    #  Gets the editor for the column of a specified object:
    #---------------------------------------------------------------------------

    def get_editor ( self, object ):
        """ Gets the editor for the column of a specified object.
        """
        return None

    #---------------------------------------------------------------------------
    #  Returns the result of comparing the column of two different objects:
    #---------------------------------------------------------------------------

    def cmp ( self, object1, object2 ):
        """ Returns the result of comparing the column of two different objects.
        """
        return cmp( object1[ self.index ], object2[ self.index ] )

