#-------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
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
#  Date:   02/29/2008
#
#-------------------------------------------------------------------------------

""" Defines the adapter classes associated with the Traits UI TabularEditor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from ..api import (Any, Bool, Color, Enum, Event, Float, Font, HasPrivateTraits,
    HasTraits, Instance, Int, Interface, List, Property, Str, cached_property,
    implements, on_trait_change)

#-------------------------------------------------------------------------------
#  'ITabularAdapter' interface:
#-------------------------------------------------------------------------------

class ITabularAdapter ( Interface ):

    # The row index of the current item being adapted:
    row = Int

    # The current column id being adapted (if any):
    column = Any

    # Current item being adapted:
    item = Any

    # The current value (if any):
    value = Any

    # The list of columns the adapter supports. The items in the list have the
    # same format as the *columns* trait in the *TabularAdapter* class, with the
    # additional requirement that the *string* values must correspond to a
    # *string* value in the associated *TabularAdapter* class.
    columns = List( Str )

    # Does the adapter know how to handle the current *item* or not:
    accepts = Bool

    # Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool

#-------------------------------------------------------------------------------
#  'AnITabularAdapter' class:
#-------------------------------------------------------------------------------

class AnITabularAdapter ( HasPrivateTraits ):

    implements( ITabularAdapter )

    #-- Implementation of the ITabularAdapter Interface ------------------------

    # The row index of the current item being adapted:
    row = Int

    # The current column id being adapted (if any):
    column = Any

    # Current item being adapted:
    item = Any

    # The current value (if any):
    value = Any

    # The list of columns the adapter supports. The items in the list have the
    # same format as the *columns* trait in the *TabularAdapter* class, with the
    # additional requirement that the *string* values must correspond to a
    # *string* value in the associated *TabularAdapter* class.
    columns = List( Str )

    # Does the adapter know how to handle the current *item* or not:
    accepts = Bool( True )

    # Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool( True )

#-------------------------------------------------------------------------------
#  'TabularAdapter' class:
#-------------------------------------------------------------------------------

class TabularAdapter ( HasPrivateTraits ):
    """ The base class for adapting list items to values that can be edited
        by a TabularEditor.
    """

    #-- Public Trait Definitions -----------------------------------------------

    # A list of columns that should appear in the table. Each entry can have one
    # of two forms: string or ( string, any ), where *string* is the UI name of
    # the column, and *any* is a value that identifies that column to the
    # adapter. Normally this value is either a trait name or an index, but it
    # can be any value that the adapter wants. If only *string* is specified,
    # then *any* is the index of the *string* within *columns*.
    columns = List()

    # Specifies the default value for a new row:
    default_value = Any( '' )

    # The default text color for table rows (even, odd, any rows):
    odd_text_color     = Color( None, update = True )
    even_text_color    = Color( None, update = True )
    default_text_color = Color( None, update = True )

    # The default background color for table rows (even, odd, any rows):
    odd_bg_color     = Color( None, update = True )
    even_bg_color    = Color( None, update = True )
    default_bg_color = Color( None, update = True )

    # Alignment to use for a specified column:
    alignment = Enum( 'left', 'center', 'right' )

    # The Python format string to use for a specified column:
    format = Str( '%s' )

    # Width of a specified column:
    width = Float( -1 )

    # Can the text value of each item be edited:
    can_edit = Bool( True )

    # The value to be dragged for a specified row item:
    drag = Property

    # Can any arbitrary value be dropped onto the tabular view:
    can_drop = Bool( False )

    # Specifies where a dropped item should be placed in the table relative to
    # the item it is dropped on:
    dropped = Enum( 'after', 'before' )

    # The font for a row item:
    font = Font( None )

    # The text color for a row item:
    text_color = Property

    # The background color for a row item:
    bg_color = Property

    # The name of the default image to use for column items:
    image = Str( None, update = True )

    # The text of a row/column item:
    text = Property

    # The content of a row/column item (may be any Python value):
    content = Property

    # The tooltip information for a row/column item:
    tooltip = Str

    # List of optional delegated adapters:
    adapters = List( ITabularAdapter, update = True )

    #-- Traits Set by the Editor -----------------------------------------------

    # The object whose trait is being edited:
    object = Instance( HasTraits )

    # The name of the trait being edited:
    name = Str

    # The row index of the current item being adapted:
    row = Int

    # The column index of the current item being adapted:
    column = Int

    # The current column id being adapted (if any):
    column_id = Any

    # Current item being adapted:
    item = Any

    # The current value (if any):
    value = Any

    #-- Private Trait Definitions ----------------------------------------------

    # Cache of attribute handlers:
    cache = Any( {} )

    # Event fired when the cache is flushed:
    cache_flushed = Event( update = True )

    # The mapping from column indices to column identifiers (defined by the
    # *columns* trait):
    column_map = Property( depends_on = 'columns' )

    # The mapping from column indices to column labels (defined by the *columns*
    # trait):
    label_map = Property( depends_on = 'columns' )

    # For each adapter, specifies the column indices the adapter handles:
    adapter_column_indices = Property( depends_on = 'adapters,columns' )

    # For each adapter, specifies the mapping from column index to column id:
    adapter_column_map = Property( depends_on = 'adapters,columns' )

    #-- Adapter methods that are sensitive to item type ------------------------

    def get_alignment ( self, object, trait, column ):
        """ Returns the alignment style to use for a specified column.
        """
        return self._result_for( 'get_alignment', object, trait, 0, column )

    def get_width ( self, object, trait, column ):
        """ Returns the width to use for a specified column.
        """
        return self._result_for( 'get_width', object, trait, 0, column )

    def get_can_edit ( self, object, trait, row ):
        """ Returns whether the user can edit a specified
            *object.trait[row]* item. A True result indicates the value
            can be edited, while a False result indicates that it cannot be
            edited.
        """
        return self._result_for( 'get_can_edit', object, trait, row, 0 )

    def get_drag ( self, object, trait, row ):
        """ Returns the 'drag' value for a specified
            *object.trait[row]* item. A result of *None* means that the
            item cannot be dragged.
        """
        return self._result_for( 'get_drag', object, trait, row, 0 )

    def get_can_drop ( self, object, trait, row, value ):
        """ Returns whether the specified *value* can be dropped on the
            specified *object.trait[row]* item. A value of **True** means the
            *value* can be dropped; and a value of **False** indicates that it
            cannot be dropped.
        """
        return self._result_for( 'get_can_drop', object, trait, row, 0, value )

    def get_dropped ( self, object, trait, row, value ):
        """ Returns how to handle a specified *value* being dropped on a
            specified *object.trait[row]* item. The possible return values are:

            'before'
                Insert the specified *value* before the dropped on item.
            'after'
                Insert the specified *value* after the dropped on item.
        """
        return self._result_for( 'get_dropped', object, trait, row, 0, value )

    def get_font ( self, object, trait, row ):
        """ Returns the font for a specified *object.trait[row]* item. A result
            of None means use the default font.
        """
        return self._result_for( 'get_font', object, trait, row, 0 )

    def get_text_color ( self, object, trait, row ):
        """ Returns the text color for a specified *object.trait[row]*
            item. A result of None means use the default text color.
        """
        return self._result_for( 'get_text_color', object, trait, row, 0 )

    def get_bg_color ( self, object, trait, row ):
        """ Returns the background color for a specified *object.trait[row]*
            item. A result of None means use the default background color.
        """
        return self._result_for( 'get_bg_color', object, trait, row, 0 )

    def get_image ( self, object, trait, row, column ):
        """ Returns the name of the image to use for a specified
            *object.trait[row].column* item. A result of None means no image
            should be used. Otherwise, the result should either be the name of
            the image, or an ImageResource item specifying the image to use.
        """
        return self._result_for( 'get_image', object, trait, row, column )

    def get_format ( self, object, trait, row, column ):
        """ Returns the Python format string to use for a specified column.
        """
        return self._result_for( 'get_format', object, trait, row, column )

    def get_text ( self, object, trait, row, column ):
        """ Returns the text to display for a specified
            *object.trait[row].column* item.
        """
        return self._result_for( 'get_text', object, trait, row, column )

    def get_content ( self, object, trait, row, column ):
        """ Returns the content to display for a specified
            *object.trait[row].column* item.
        """
        return self._result_for( 'get_content', object, trait, row, column )

    def set_text ( self, object, trait, row, column, text ):
        """ Sets the text for a specified *object.trait[row].column* item to
            *text*.
        """
        self._result_for( 'set_text', object, trait, row, column, text )

    def get_tooltip ( self, object, trait, row, column ):
        """ Returns the tooltip for a specified row.
        """
        return self._result_for( 'get_tooltip', object, trait, row, column )

    #-- Adapter methods that are not sensitive to item type --------------------

    def get_item ( self, object, trait, row ):
        """ Returns the value of the *object.trait[row]* item.
        """
        try:
            return getattr( object, trait )[ row ]
        except:
            return None

    def len ( self, object, trait ):
        """ Returns the number of items in the specified *object.trait* list.
        """
        return len( getattr( object, trait ) )

    def get_default_value ( self, object, trait ):
        """ Returns a new default value for the specified *object.trait* list.
        """
        return self.default_value

    def delete ( self, object, trait, row ):
        """ Deletes the specified *object.trait[row]* item.
        """
        del getattr( object, trait )[ row ]

    def insert ( self, object, trait, row, value ):
        """ Inserts a new value at the specified *object.trait[row]* index.
        """
        getattr( object, trait ) [ row: row ] = [ value ]

    def get_column ( self, object, trait, index ):
        """ Returns the column id corresponding to a specified column index.
        """
        self.object, self.name = object, trait
        return self.column_map[ index ]

    #-- Property Implementations -----------------------------------------------

    def _get_drag ( self ):
        return self.item

    def _get_text_color ( self ):
        if (self.row % 2) == 1:
            return self.even_text_color_ or self.default_text_color

        return self.odd_text_color or self.default_text_color_

    def _get_bg_color ( self ):
        if (self.row % 2) == 1:
            return self.even_bg_color_ or self.default_bg_color_

        return self.odd_bg_color or self.default_bg_color_

    def _get_text ( self ):
        return self.get_format(
            self.object, self.name, self.row, self.column ) % self.get_content(
            self.object, self.name, self.row, self.column )

    def _set_text ( self, value ):
        if isinstance( self.column_id, int ):
            self.item[ self.column_id ] = self.value
        else:
            # Convert value to the correct trait type.
            try:
                trait_handler = self.item.trait(self.column_id).handler
                setattr( self.item, self.column_id,
                                    trait_handler.evaluate(self.value))
            except:
                setattr( self.item, self.column_id, value )

    def _get_content ( self ):
        if isinstance( self.column_id, int ):
            return self.item[ self.column_id ]

        return getattr( self.item, self.column_id )

    #-- Property Implementations -----------------------------------------------

    @cached_property
    def _get_column_map ( self ):
        map = []
        for i, value in enumerate( self.columns ):
            if isinstance( value, basestring ):
                map.append( i )
            else:
                map.append( value[1] )

        return map

    @cached_property
    def _get_label_map ( self ):
        map = []
        for i, value in enumerate( self.columns ):
            if isinstance( value, basestring ):
                map.append( value )
            else:
                map.append( value[0] )

        return map

    @cached_property
    def _get_adapter_column_indices ( self ):
        labels = self.label_map
        map    = []
        for adapter in self.adapters:
            indices = []
            for label in adapter.columns:
                if not isinstance( label, basestring ):
                    label = label[0]

                indices.append( labels.index( label ) )
            map.append(indices)
        return map

    @cached_property
    def _get_adapter_column_map ( self ):
        labels = self.label_map
        map    = []
        for adapter in self.adapters:
            mapping = {}
            for label in adapter.columns:
                id = None
                if not isinstance( label, basestring ):
                    label, id = label

                key = labels.index( label )
                if id is None:
                    id = key

                mapping[ key ] = id

            map.append( mapping )

        return map

    #-- Private Methods --------------------------------------------------------

    def _result_for ( self, name, object, trait, row, column, value = None ):
        """ Returns/Sets the value of the specified *name* attribute for the
            specified *object.trait[row].column* item.
        """
        self.object    = object
        self.name      = trait
        self.row       = row
        self.column    = column
        self.column_id = column_id = self.column_map[ column ]
        self.value     = value
        self.item      = item = self.get_item( object, trait, row )
        item_class     = item.__class__
        key            = '%s:%s:%d' % ( item_class.__name__, name, column )
        handler        = self.cache.get( key )
        if handler is not None:
            return handler()

        prefix     = name[:4]
        trait_name = name[4:]

        for i, adapter in enumerate( self.adapters ):
            if column in self.adapter_column_indices[i]:
                adapter.row    = row
                adapter.item   = item
                adapter.value  = value
                adapter.column = column_id = self.adapter_column_map[i][column]
                if adapter.accepts:
                    get_name = '%s_%s' % ( column_id, trait_name )
                    if adapter.trait( get_name ) is not None:
                        if prefix == 'get_':
                            handler = lambda: getattr( adapter.set(
                                row  = self.row, column = column_id,
                                item = self.item ), get_name )
                        else:
                            handler = lambda: setattr( adapter.set(
                                row  = self.row, column = column_id,
                                item = self.item ), get_name, self.value )

                        if adapter.is_cacheable:
                            break

                        return handler()
        else:
            if item is not None and hasattr(item_class, '__mro__'):
                for klass in item_class.__mro__:
                    handler = (self._get_handler_for( '%s_%s_%s' %
                          ( klass.__name__, column_id, trait_name ), prefix ) or
                        self._get_handler_for( '%s_%s' %
                          ( klass.__name__, trait_name ), prefix ))
                    if handler is not None:
                        break

            if handler is None:
                handler = (self._get_handler_for( '%s_%s' % ( column_id,
                              trait_name ), prefix ) or
                           self._get_handler_for( trait_name, prefix ))

        self.cache[ key ] = handler
        return handler()

    def _get_handler_for ( self, name, prefix ):
        """ Returns the handler for a specified trait name (or None if not
            found).
        """
        if self.trait( name ) is not None:
            if prefix == 'get_':
                return lambda: getattr( self, name )

            return lambda: setattr( self, name, self.value )

        return None

    @on_trait_change( 'columns,adapters.+update' )
    def _flush_cache ( self ):
        """ Flushes the cache when the columns or any trait on any adapter
            changes.
        """
        self.cache = {}
        self.cache_flushed = True

