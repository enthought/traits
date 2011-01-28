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
#  Date:   10/07/2004
#
#------------------------------------------------------------------------------

""" Defines the Item class, which is used to represent a single item within
    a Traits-based user interface.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

import re

from string import find, rfind

from ..api import (Bool, Callable, Constant, Delegate, Float, Instance,
    Range, Str, Undefined,)

from ..trait_base import user_name_for

from .view_element import ViewSubElement

from .ui_traits import convert_theme, ContainerDelegate, EditorStyle

from .editor_factory import EditorFactory

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Pattern of all digits:
all_digits = re.compile( r'\d+' )

# Pattern for finding size infomation embedded in an item description:
size_pat = re.compile( r"^(.*)<(.*)>(.*)$", re.MULTILINE | re.DOTALL )

# Pattern for finding tooltip infomation embedded in an item description:
tooltip_pat = re.compile( r"^(.*)`(.*)`(.*)$", re.MULTILINE | re.DOTALL )

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Reference to an EditorFactory:
ItemEditor = Instance( EditorFactory, allow_none = True )

# Amount of padding to add around an item:
Padding = Range( -15, 15, 0, desc = 'amount of padding to add around item' )

#-------------------------------------------------------------------------------
#  'Item' class:
#-------------------------------------------------------------------------------

class Item ( ViewSubElement ):
    """ An element in a Traits-based user interface.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # A unique identifier for the item. If not set, it defaults to the value
    # of **name**.
    id = Str

    # User interface label for the item in the GUI. If this attribute is not
    # set, the label is the value of **name** with slight modifications:
    # underscores are replaced by spaces, and the first letter is capitalized.
    # If an item's **name** is not specified, its label is displayed as
    # static text, without any editor widget.
    label = Str

    # Name of the trait the item is editing:
    name = Str

    # Help text describing the purpose of the item. The built-in help handler
    # displays this text in a pop-up window if the user clicks the widget's
    # label. View-level help displays the help text for all items in a view.
    # If this attribute is not set, the built-in help handler generates a
    # description based on the trait definition.
    help = Str

    # The HasTraits object whose trait attribute the item is editing:
    object = ContainerDelegate

    # Presentation style for the item:
    style = ContainerDelegate

    # Docking style for the item:
    dock = ContainerDelegate

    # Image to display on notebook tabs:
    image = ContainerDelegate

    # The theme to use for the item itself:
    item_theme = ContainerDelegate

    # The theme to use for the item's label:
    label_theme = ContainerDelegate

    # Category of elements dragged from view:
    export = ContainerDelegate

    # Should a label be displayed for the item?
    show_label = Delegate( 'container', 'show_labels' )

    # Editor to use for the item:
    editor = ItemEditor

    # Should the item use extra space along its Group's layout axis? If set to
    # True, the widget expands to fill any extra space that is available in the
    # display. If set to True for more than one item in the same View, any extra
    # space is divided between them. If set to False, the widget uses only
    # whatever space it is explicitly (or implicitly) assigned. The default
    # value of Undefined means that the use (or non-use) of extra space will be
    # determined by the editor associated with the item.
    resizable = Bool( Undefined )

    # Should the item use extra space along its Group's layout axis? For
    # example, it a vertical group, should an item expand vertically to use
    # any extra space available in the group?
    springy = Bool( False )

    # Should the item use any extra space along its Group's non-layout
    # orientation? For example, in a vertical group, should an item expand
    # horizontally to the full width of the group? If left to the default value
    # of Undefined, the decision will be left up to the associated item editor.
    full_size = Bool( Undefined )

    # Should the item's label use emphasized text? If the label is not shown,
    # this attribute is ignored.
    emphasized = Bool( False )

    # Should the item receive focus initially?
    has_focus = Bool( False )

    # Pre-condition for including the item in the display. If the expression
    # evaluates to False, the item is not defined in the display. Conditions
    # for **defined_when** are evaluated only once, when the display is first
    # constructed. Use this attribute for conditions based on attributes that
    # vary from object to object, but that do not change over time. For example,
    # displaying a 'maiden_name' item only for female employees in a company
    # database.
    defined_when = Str

    # Pre-condition for showing the item. If the expression evaluates to False,
    # the widget is not visible (and disappears if it was previously visible).
    # If the value evaluates to True, the widget becomes visible. All
    # **visible_when** conditions are checked each time that any trait value
    # is edited in the display. Therefore, you can use **visible_when**
    # conditions to hide or show widgets in response to user input.
    visible_when = Str

    # Pre-condition for enabling the item. If the expression evaluates to False,
    # the widget is disabled, that is, it does not accept input. All
    # **enabled_when** conditions are checked each time that any trait value
    # is edited in the display. Therefore, you can use **enabled_when**
    # conditions to enable or disable widgets in response to user input.
    enabled_when = Str

    # Amount of extra space, in pixels, to add around the item. Values must be
    # integers between -15 and 15. Use negative values to subtract from the
    # default spacing.
    padding = Padding

    # Tooltip to display over the item, when the mouse pointer is left idle
    # over the widget. Make this text as concise as possible; use the **help**
    # attribute to provide more detailed information.
    tooltip = Str

    # A Callable to use for formatting the contents of the item. This function
    # or method is called to create the string representation of the trait value
    # to be edited. If the widget does not use a string representation, this
    # attribute is ignored.
    format_func = Callable

    # Python format string to use for formatting the contents of the item.
    # The format string is applied to the string representation of the trait
    # value before it is displayed in the widget. This attribute is ignored if
    # the widget does not use a string representation, or if the
    # **format_func** is set.
    format_str = Str

    # Requested width of the editor (in pixels or fraction of available width).
    # For pixel values (i.e. values not in the range from 0.0 to 1.0), the
    # actual displayed width is at least the maximum of **width** and the
    # optimal width of the widget as calculated by the GUI toolkit. Specify a
    # negative value to ignore the toolkit's optimal width. For example, use
    # -50 to force a width of 50 pixels. The default value of -1 ensures that
    # the toolkit's optimal width is used.
    #
    # A value in the range from 0.0 to 1.0 specifies the fraction of the
    # available width to assign to the editor. Note that the value is not an
    # absolute value, but is relative to other item's whose **width** is also
    # in the 0.0 to 1.0 range. For example, if you have two item's with a width
    # of 0.1, and one item with a width of 0.2, the first two items will each
    # receive 25% of the available width, while the third item will receive
    # 50% of the available width. The available width is the total width of the
    # view minus the width of any item's with fixed pixel sizes (i.e. width
    # values not in the 0.0 to 1.0 range).
    width = Float( -1.0 )

    # Requested height of the editor (in pixels or fraction of available
    # height). For pixel values (i.e. values not in the range from 0.0 to 1.0),
    # the actual displayed height is at least the maximum of **height** and the
    # optimal height of the widget as calculated by the GUI toolkit. Specify a
    # negative value to ignore the toolkit's optimal height. For example, use
    # -50 to force a height of 50 pixels. The default value of -1 ensures that
    # the toolkit's optimal height is used.
    #
    # A value in the range from 0.0 to 1.0 specifies the fraction of the
    # available height to assign to the editor. Note that the value is not an
    # absolute value, but is relative to other item's whose **height** is also
    # in the 0.0 to 1.0 range. For example, if you have two item's with a height
    # of 0.1, and one item with a height of 0.2, the first two items will each
    # receive 25% of the available height, while the third item will receive
    # 50% of the available height. The available height is the total height of
    # the view minus the height of any item's with fixed pixel sizes (i.e.
    # height values not in the 0.0 to 1.0 range).
    height = Float( -1.0 )

    # The extended trait name of the trait containing the item's invalid state
    # status (passed through to the item's editor):
    invalid = Str

    #---------------------------------------------------------------------------
    #  Initialize the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, value = None, **traits ):
        """ Initializes the item object.
        """
        super( Item, self ).__init__( **traits )

        if value is None:
            return

        if not isinstance( value, basestring ):
            raise TypeError, ("The argument to Item must be a string of the "
                 "form: [id:][object.[object.]*][name]['['label']']`tooltip`"
                 "[<width[,height]>][#^][$|@|*|~|;style]")

        value, empty = self._parse_label( value )
        if empty:
            self.show_label = False

        value = self._parse_style( value )
        value = self._parse_size(  value )
        value = self._parse_tooltip( value )
        value = self._option( value, '#',  'resizable',  True )
        value = self._option( value, '^',  'emphasized', True )
        value = self._split( 'id',     value, ':', find,  0, 1 )
        value = self._split( 'object', value, '.', rfind, 0, 1 )

        if value != '':
            self.name = value

    #---------------------------------------------------------------------------
    #  Returns whether or not the object is replacable by an Include object:
    #---------------------------------------------------------------------------

    def is_includable ( self ):
        """ Returns a Boolean indicating whether the object is replaceable by an
            Include object.
        """
        return (self.id != '')

    #---------------------------------------------------------------------------
    #  Returns whether or not the Item represents a spacer or separator:
    #---------------------------------------------------------------------------

    def is_spacer ( self ):
        """ Returns True if the item represents a spacer or separator.
        """
        name = self.name.strip()

        return ((name == '') or (name == '_') or
                (all_digits.match( name ) is not None))

    #---------------------------------------------------------------------------
    #  Gets the help text associated with the Item in a specified UI:
    #---------------------------------------------------------------------------

    def get_help ( self, ui ):
        """ Gets the help text associated with the Item in a specified UI.
        """
        # Return 'None' if the Item is a separator or spacer:
        if self.is_spacer():
            return None

        # Otherwise, it must be a trait Item:
        if self.help != '':
            return self.help

        object = eval( self.object_, globals(), ui.context )

        return object.base_trait( self.name ).get_help()

    #---------------------------------------------------------------------------
    #  Gets the label to use for a specified Item in a specified UI:
    #---------------------------------------------------------------------------

    def get_label ( self, ui ):
        """ Gets the label to use for a specified Item.
        """
        # Return 'None' if the Item is a separator or spacer:
        if self.is_spacer():
            return None

        label = self.label
        if label != '':
            return label

        name   = self.name
        object = eval( self.object_, globals(), ui.context )
        trait  = object.base_trait( name )
        label  = user_name_for( name )
        tlabel = trait.label
        if tlabel is None:
            return label

        if isinstance( tlabel, basestring ):
            if tlabel[0:3] == '...':
                return label + tlabel[3:]
            if tlabel[-3:] == '...':
                return tlabel[:-3] + label
            if self.label != '':
                return self.label
            return tlabel

        return tlabel( object, name, label )

    #---------------------------------------------------------------------------
    #  Returns an id used to identify the item:
    #---------------------------------------------------------------------------

    def get_id ( self ):
        """ Returns an ID used to identify the item.
        """
        if self.id != '':
            return self.id

        return self.name

    #---------------------------------------------------------------------------
    #  Parses a '<width,height>' value from the string definition:
    #---------------------------------------------------------------------------

    def _parse_size ( self, value ):
        """ Parses a '<width,height>' value from the string definition.
        """
        match = size_pat.match( value )
        if match is not None:
            data  = match.group( 2 )
            value = match.group( 1 ) + match.group( 3 )
            col   = data.find( ',' )
            if col < 0:
                self._set_float( 'width', data )
            else:
                self._set_float( 'width',  data[ : col ] )
                self._set_float( 'height', data[ col + 1: ] )

        return value

    #---------------------------------------------------------------------------
    #  Parses a '`tooltip`' value from the string definition:
    #---------------------------------------------------------------------------

    def _parse_tooltip ( self, value ):
        """ Parses a *tooltip* value from the string definition.
        """
        match = tooltip_pat.match( value )
        if match is not None:
            self.tooltip = match.group( 2 )
            value        = match.group( 1 ) + match.group( 3 )

        return value

    #---------------------------------------------------------------------------
    #  Sets a specified trait to a specified string converted to a float:
    #---------------------------------------------------------------------------

    def _set_float ( self, name, value ):
        """ Sets a specified trait to a specified string converted to a float.
        """
        value = value.strip()
        if value != '':
            setattr( self, name, float( value ) )

    #---------------------------------------------------------------------------
    #  Returns a 'pretty print' version of the Item:
    #---------------------------------------------------------------------------

    def __repr__ ( self ):
        """ Returns a "pretty print" version of the Item.
        """

        options = self._repr_options( 'id', 'object', 'label', 'style',
                                      'show_label', 'width', 'height' )
        if options is None:
            return "Item( '%s' )" % self.name

        return "Item( '%s'\n%s\n)" % (
               self.name, self._indent( options, '      ' ) )

#-------------------------------------------------------------------------------
#  'UItem' class:
#-------------------------------------------------------------------------------

class UItem ( Item ):
    """ An Item that has no label.
    """

    show_label = Bool( False )

#-------------------------------------------------------------------------------
#  'Custom' class:
#-------------------------------------------------------------------------------

class Custom ( Item ):
    """ An Item using a 'custom' style.
    """

    style = EditorStyle( 'custom' )

#-------------------------------------------------------------------------------
#  'UCustom' class:
#-------------------------------------------------------------------------------

class UCustom ( Custom ):
    """ An Item using a 'custom' style with no label.
    """

    show_label = Bool( False )

#-------------------------------------------------------------------------------
#  'Readonly' class:
#-------------------------------------------------------------------------------

class Readonly ( Item ):
    """ An Item using a 'readonly' style.
    """

    style = EditorStyle( 'readonly' )

#-------------------------------------------------------------------------------
#  'UReadonly' class:
#-------------------------------------------------------------------------------

class UReadonly ( Readonly ):
    """ An Item using a 'readonly' style with no label.
    """

    show_label = Bool( False )

#-------------------------------------------------------------------------------
#  'Label' class:
#-------------------------------------------------------------------------------

class Label ( Item ):
    """ An item that is a label.
    """

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, label, item_theme = None, **traits ):
        super( Label, self ).__init__(
            label      = label,
            item_theme = convert_theme( item_theme ),
            **traits
        )

#-------------------------------------------------------------------------------
#  'Heading' class:
#-------------------------------------------------------------------------------

class Heading ( Label ):
    """ An item that is a fancy label.
    """

    # Override the 'style' trait to default to the fancy 'custom' style:
    style = Constant( 'custom' )

#-------------------------------------------------------------------------------
#  'Spring' class:
#-------------------------------------------------------------------------------

class Spring ( Item ):
    """ An item that is a layout "spring".
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Name of the trait the item is editing
    name = 'spring'

    # Should a label be displayed?
    show_label = Bool( False )

    # Editor to use for the item
    editor = Instance( 'enthought.traits.ui.api.NullEditor', () )

    # Should the item use extra space along its Group's layout orientation?
    springy = True

# A pre-defined spring for convenience
spring = Spring()

