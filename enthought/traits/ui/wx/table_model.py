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
# Date: 07/01/2005
#
#------------------------------------------------------------------------------
""" Defines the table grid model used by the table editor based on the PyFace
grid control.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, HasPrivateTraits, Any, Str, List, Instance, Event, false

from enthought.traits.ui.api \
    import Editor

from enthought.traits.ui.table_filter \
    import TableFilter

from enthought.traits.ui.ui_traits \
    import SequenceTypes

from enthought.pyface.grid.api \
    import GridModel, GridSortEvent

from enthought.pyface.grid.grid_cell_renderer \
    import GridCellRenderer

from enthought.pyface.grid.trait_grid_cell_adapter \
    import TraitGridCellAdapter

from enthought.util.wx.do_later \
    import do_later

#-------------------------------------------------------------------------------
#  'TraitGridSelection' class:
#-------------------------------------------------------------------------------

class TraitGridSelection ( HasPrivateTraits ):
    """ Structure for holding specification information. """

    # The selected object
    obj = Any

    # The specific trait selected on the object
    name = Str

#-------------------------------------------------------------------------------
#  'TableModel' class:
#-------------------------------------------------------------------------------

class TableModel ( GridModel ):
    """ Model for table data.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The editor that created this model
    editor = Instance( Editor )

    # The current filter
    filter = Instance( TableFilter, allow_none = True )

    # Current filter summary message
    filter_summary = Str( 'All items' )

    # Display the table items in reverse order?
    reverse = false

    # Event fired when the table has been sorted
    sorted = Event

    # The current 'auto_add' row
    auto_add_row = Any

    #---------------------------------------------------------------------------
    #  'object' interface:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, **traits ):
        """ Initializes the object.
        """
        super( TableModel, self ).__init__( **traits )

        # Attach trait handlers to the list object:
        editor = self.editor
        object = editor.context_object
        name   = ' ' + editor.extended_name

        # Set up listeners for any of the model data changing:
        object.on_trait_change( self._on_data_changed, name, dispatch = 'ui' )
        object.on_trait_change( self.fire_content_changed, name + '.+', 
                                dispatch = 'ui' )

        # Set up listeners for any column definitions changing:
        editor.on_trait_change( self.update_columns, 'columns',
                                dispatch = 'ui' )
        editor.on_trait_change( self.update_columns, 'columns_items',
                                dispatch = 'ui' )

        # Initialize the current filter from the editor's default filter:
        self.filter = editor.filter

        # If we are using 'auto_add' mode, create the first 'auto_add' row:
        if editor.auto_add:
            self.auto_add_row = row = editor.create_new_row()
            if row is not None:
                row.on_trait_change( self.on_auto_add_row, dispatch = 'ui' )

    #---------------------------------------------------------------------------
    #  'TableModel' interface:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Disposes of the model when it is no longer needed:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the model when it is no longer needed.
        """
        editor = self.editor
        object = editor.context_object
        name   = ' ' + editor.extended_name

        # Remove listeners for any of the model data changing:
        object.on_trait_change( self._on_data_changed, name, remove = True )
        object.on_trait_change( self.fire_content_changed, name + '.+', 
                                remove = True )

        # Remove listeners for any column definitions changing:
        editor.on_trait_change( self.update_columns, 'columns', remove = True )
        editor.on_trait_change( self.update_columns, 'columns_items',
                                remove = True )

        # Make sure we have removed listeners from the current filter also:
        if self.filter is not None:
            self.filter.on_trait_change( self._filter_modified, remove = True )

    #---------------------------------------------------------------------------
    #  Returns all model items matching the current filter:
    #---------------------------------------------------------------------------

    def get_filtered_items ( self ):
        """ Returns all model items matching the current filter.
        """
        return self.__filtered_items()

    #---------------------------------------------------------------------------
    #  Returns a single specified item from those items matching the current
    #  filter:
    #---------------------------------------------------------------------------

    def get_filtered_item ( self, index = 0 ):
        """ Returns a single specified item from those items matching the
            current filter.
        """
        try:
            return self.__filtered_items()[ index ]
        except:
            from enthought.logger import logger

            logger.error( 'TableModel error: Request for invalid row %d out of '
                          '%d' % ( index, len( self.__filtered_items() ) ) )
            return None

    #---------------------------------------------------------------------------
    #  Inserts an object after a specified filtered index:
    #---------------------------------------------------------------------------

    def insert_filtered_item_after ( self, index, item ):
        """ Inserts an object after a specified filtered index.
        """
        mapped_index = 0
        n            = len( self._filtered_map )
        if index >= n:
            if (index != 0) or (n != 0):
                raise IndexError
        elif index >= 0:
            mapped_index = self._filtered_map[ index ] + 1
        self.__items().insert( mapped_index, item )
        sorted = self._sort_model()
        if sorted:
            mapped_index = self.__items().index( item )
        self._filtered_cache = None
        return ( mapped_index, sorted )

    #---------------------------------------------------------------------------
    #  Deletes the object at the specified filtered index:
    #---------------------------------------------------------------------------

    def delete_filtered_item_at ( self, index ):
        """ Deletes the object at the specified filtered index.
        """
        if index >= len( self._filtered_map ):
            raise IndexError
        mapped_index = self._filtered_map[ index ]
        items        = self.__items()
        object       = items[ mapped_index ]
        del items[ mapped_index ]
        self._filtered_cache = None
        return ( mapped_index, object )

    #---------------------------------------------------------------------------
    #  Updates the table view when columns have been changed:
    #---------------------------------------------------------------------------

    def update_columns ( self ):
        """ Updates the table view when columns have been changed.
        """
        self._columns = None
        self.fire_structure_changed()
        self.editor.refresh()

    #---------------------------------------------------------------------------
    #  Resets any sorting being performed on the underlying model:
    #---------------------------------------------------------------------------

    def no_column_sort ( self ):
        """ Resets any sorting being performed on the underlying model.
        """
        self._sorter = self._filtered_cache = None
        self.column_sorted = GridSortEvent(index = -1)
        #self.fire_structure_changed()

    #---------------------------------------------------------------------------
    #  Event handlers:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles a new filter being assigned:
    #---------------------------------------------------------------------------

    def _filter_changed ( self, old, new ):
        """ Handles a new filter being assigned.
        """
        if old is not None:
            old.on_trait_change( self._filter_modified, remove = True )
            
        if new is not None:
            new.on_trait_change( self._filter_modified, dispatch = 'ui' )
            
        self._filter_modified()

    #---------------------------------------------------------------------------
    #  Handles the contents of the filter being changed:
    #---------------------------------------------------------------------------

    def _filter_modified ( self ):
        """ Handles the contents of the filter being changed.
        """
        self._filtered_cache = None
        self.fire_structure_changed()

    #---------------------------------------------------------------------------
    #  Handles the user modifying the current 'auto_add' mode row:
    #---------------------------------------------------------------------------

    def on_auto_add_row ( self ):
        """ Handles the user modifying the current 'auto_add' mode row.
        """
        object = self.auto_add_row
        object.on_trait_change( self.on_auto_add_row, remove = True )
        self.auto_add_row = row = self.editor.create_new_row()
        if row is not None:
            row.on_trait_change( self.on_auto_add_row, dispatch = 'ui' )
        do_later( self.editor.add_row, object,
                                       len( self.get_filtered_items() ) - 2 )

    #---------------------------------------------------------------------------
    #  'GridModel' interface:
    #---------------------------------------------------------------------------

    def get_column_count ( self ):
        """ Returns the number of columns for this table.
        """
        return len( self.__get_columns() )

    def get_column_name ( self, index ):
        """ Returns the label of the column specified by the (zero-based) index.
        """
        return self.__get_column( index ).get_label()

    def get_column_size ( self, index ):
        """ Returns the size in pixels of the column indexed by *index*.
            A value of -1 or None means to use the default. """
        return self.__get_column( index ).get_width()

    def get_cols_drag_value ( self, cols ):
        """ Returns the value to use when the specified columns are dragged or
            copied and pasted. The parameter *cols* is a list of column indexes.
        """
        return [ self.__get_data_column( col ) for col in cols ]

    def get_cols_selection_value ( self, cols ):
        """ Returns a list of TraitGridSelection objects containing the
            objects corresponding to the grid rows and the traits corresponding
            to the specified columns.
        """
        values = []
        for obj in self.__items( False ):
            values.extend( [ TraitGridSelection(
                                 obj  = obj,
                                 name = self.__get_column_name( col ) )
                             for col in cols ] )
        return values

    def sort_by_column ( self, col, reverse = False ):
        """ Sorts the model data by the column indexed by *col*.
        """
        # Make sure we allow sorts by column:
        factory = self.editor.factory
        if not factory.sortable:
            return

        # Flush the object cache:
        self._filtered_cache = None

        # Cache the sorting information for later:
        self._sorter  = self.__get_column( col ).cmp
        self._reverse = reverse

        # If model sorting is requested, do it now:
        self._sort_model()

        # Indicate the we have been sorted:
        self.sorted = True

        self.column_sorted = GridSortEvent( index    = col,
                                            reversed = reverse )

    def is_column_read_only ( self, index ):
        """ Returns True if the column specified by the zero-based *index* is
            read-only.
        """
        return (not self.__get_column( index ).editable)

    def get_row_count ( self ):
        """ Return the number of rows for this table.
        """
        return len( self.__filtered_items() )

    def get_row_name ( self, index ):
        """ Return the name of the row specified by the (zero-based) *index*.
        """
        return '<undefined>'

    def get_rows_drag_value ( self, rows ):
        """ Returns the value to use when the specified rows are dragged or
            copied and pasted. The parameter *rows* is a list of row indexes.
            If there is only one row listed, then return the corresponding trait
            object. If more than one row is listed, then return a list of objects.
        """
        items = self.__filtered_items()
        return [ items[ row ] for row in rows ]

    def get_rows_selection_value ( self, rows ):
        """ Returns a list of TraitGridSelection objects containing the
        object corresponding to the selected rows.
        """
        items = self.__filtered_items()
        return [ TraitGridSelection( obj = items[ row ] ) for row in rows ]

    def is_row_read_only ( self, index ):
        """ Returns True if the row specified by the zero-based *index* is
            read-only.
        """
        return False

    def get_cell_editor ( self, row, col ):
        """ Returns the editor for the specified cell.
        """

        column = self.__get_column( col )
        object = self.get_filtered_item( row )
        editor = column.get_editor( object )
        if editor is None:
            return None
        return TraitGridCellAdapter( editor, column.get_object( object ),
                             column.name, '', context = self.editor.ui.context )

    def get_cell_renderer ( self, row, col ):
        """ Returns the renderer for the specified cell.
        """
        return self.__get_column( col ).get_renderer(
                   self.get_filtered_item( row ) )

    def get_cell_bg_color ( self, row, col ):
        """ Returns a wxColour object specifying the background color
            of the specified cell. """
        obj = self.get_filtered_item( row )
        return self.__get_column( col ).get_cell_color( obj )

    def get_cell_text_color ( self, row, col ):
        """ Returns a wxColour object specifying the text color
            of the specified cell. """

        obj = self.get_filtered_item( row )
        return self.__get_column( col ).get_text_color( obj )

    def get_cell_drag_value ( self, row, col ):
        """ Returns the value to use when the specified cell is dragged or
            copied and pasted.
        """
        return self.__get_column( col ).get_raw_value(
                                            self.get_filtered_item( row ) )

    def get_cell_selection_value ( self, row, col ):
        """ Returns a TraitGridSelection object specifying the data stored
            in the table at (*row*, *col*).
        """
        return TraitGridSelection( obj  = self.get_filtered_item( row ),
                                   name = self.__get_column_name( col ) )

    def resolve_selection ( self, selection_list ):
        """ Returns a list of (row, col) grid-cell coordinates that
            correspond to the objects in *selection_list*. For each coordinate,
            if the row is -1, it indicates that the entire column is selected.
            Likewise coordinates with a column of -1 indicate an entire row
            that is selected. For the TableModel, the objects in
            *selection_list* must be TraitGridSelection objects.
        """
        items = self.__filtered_items()
        cells = []
        for selection in selection_list:
            try:
                row = items.index( selection.obj )
            except ValueError:
                continue

            column = -1
            if selection.name != '':
                column = self._get_column_index_by_trait( selection.name )
                if column is None:
                    continue

            cells.append( ( row, column ) )

        return cells

    def get_cell_context_menu ( self, row, col ):
        """ Returns a Menu object that generates the appropriate context
            menu for this cell.
        """
        column = self.__get_column( col )
        menu   = column.get_menu( self.get_filtered_item( row ) )
        editor = self.editor
        if menu is None:
            menu = editor.factory.menu
        if menu is not None:
            editor.prepare_menu( row, column )
            return ( menu, editor )
        return None

    def get_value ( self, row, col ):
        """ Returns the value stored in the table at (*row*, *col*).
        """
        object = self.get_filtered_item( row )
        if object is self.auto_add_row:
            return ''

        value   = self.__get_column( col ).get_value( object )
        formats = self.__get_column_formats( col )

        if (value is not None) and (formats is not None):
            format = formats.get( type( value ) )
            if format is not None:
                try:
                    if callable( format ):
                        value = format( value )
                    else:
                        value = format % value
                except:
                    pass

        return value

    def is_valid_cell_value ( self, row, col, value ):
        """ Tests whether *value* is valid for the cell at (*row*, *col*).
        Returns True if value is acceptable, and False otherwise. """
        return self.__get_column( col ).is_droppable(
                   self.get_filtered_item( row ), value )

    def is_cell_empty ( self, row, col ):
        """ Returns True if the cell at (*row*, *col*) has a None value, and
            False otherwise.
        """
        return (self.get_value( row, col ) is None)

    def is_cell_read_only ( self, row, col ):
        """ Returns True if the cell at (*row*, *col*) is read-only, and False
            otherwise.
        """
        return (not self.__get_column( col ).is_editable(
                   self.get_filtered_item( row ) ))

    def get_cell_bg_color ( self, row, col ):
        """ Returns a wxColour object specifying the background color
            of the specified cell.
        """
        return self.__get_column( col ).get_cell_color(
                   self.get_filtered_item( row ) )

    def get_cell_text_color ( self, row, col ):
        """ Returns a wxColour object specifying the text color of the
            specified cell.
        """
        return self.__get_column( col ).get_text_color(
                   self.get_filtered_item( row ) )

    def get_cell_font ( self, row, col ):
        """ Returns a wxFont object specifying the font of the specified cell.
        """
        return self.__get_column( col ).get_text_font(
                   self.get_filtered_item( row ) )

    def get_cell_halignment ( self, row, col ):
        """ Returns a string specifying the horizontal alignment of the
            specified cell.

            Returns 'left' for left alignment, 'right' for right alignment,
            or 'center' for center alignment.
        """
        return self.__get_column( col ).get_horizontal_alignment(
                   self.get_filtered_item( row ) )

    def get_cell_valignment ( self, row, col ):
        """ Returns a string specifying the vertical alignment of the
            specified cell.

            Returns 'top' for top alignment, 'bottom' for bottom alignment,
            or 'center' for center alignment.
        """
        return self.__get_column( col ).get_vertical_alignment(
                   self.get_filtered_item( row ) )

    #---------------------------------------------------------------------------
    #  Protected 'GridModel' interface:
    #---------------------------------------------------------------------------

    def _insert_rows ( self, pos, num_rows ):
        """ Inserts *num_rows* at *pos*; fires an event only if a factory
        method for new rows is defined or the model is not empty. Otherwise,
        it returns 0.
        """
        count = 0

        factory = self.editor.factory.row_factory
        if factory is None:
            items = self.__items( False )
            if len( items ) > 0:
                factory = items[0].__class__

        if factory is not None:
            new_data = [ x for x in [ factory() for i in range( num_rows ) ]
                         if x is not None ]
            if len( new_data ) > 0:
                count           = self._insert_rows_into_model( pos, new_data )
                self.rows_added = ( 'added', pos, new_data )

        return count

    def _delete_rows ( self, pos, num_rows ):
        """ Removes rows *pos* through *pos* + *num_rows* from the model.
        """
        row_count = self.get_rows_count()
        if (pos + num_rows) > row_count:
            num_rows = rows_count - pos

        return self._delete_rows_from_model( pos, num_rows )

    def _set_value ( self, row, col, value ):
        """ Sets the value of the cell at (*row*, *col*) to *value*.

            Raises a ValueError if the value is vetoed or the cell at
            the specified position does not exist.
        """
        new_rows = 0
        column   = self.__get_column( col )
        obj      = None
        try:
            obj = self.get_filtered_item( row )
        except:
            # Add a new row:
            new_rows = self._insert_rows( self.get_row_count(), 1 )
            if new_rows > 0:
                # Now set the value on the new object:
                try:
                    obj = self.get_filtered_item( self.get_row_count() - 1 )
                except:
                    # fixme: what do we do in this case? veto the set somehow?
                    # raise an exception?
                    pass

        if obj is not None:
            self._set_data_on_row( obj, column, value )

        return new_rows

    #---------------------------------------------------------------------------
    #  Protected interface:
    #---------------------------------------------------------------------------

    def _set_data_on_row ( self, row, column, value ):
        """ Sets the cell specified by (*row*, *col*) to *value, which
            can be either a member of the row object, or a no-argument method
            on that object.
        """
        column.set_value( row, value )

    def _insert_rows_into_model ( self, pos, new_data ):
        """ Inserts the given new rows into the model.
        """
        raw_pos = self.__raw_index_of( pos )
        self.__items()[ raw_pos: raw_pos ] = new_data

    def _delete_rows_from_model ( self, pos, num_rows ):
        """ Deletes the specified rows from the model.
        """
        raw_rows = [ self.__raw_index_of( i )
                     for i in range( pos, pos + num_rows ) ]
        raw_rows.sort()
        raw_rows.reverse()
        items = self.__items()
        for row in raw_rows:
            del items[ row ]

        return num_rows

    #---------------------------------------------------------------------------
    #  Trait event handlers:
    #---------------------------------------------------------------------------

    def _on_data_changed ( self ):
        """ Forces the grid to refresh when the underlying list changes.
        """
        # Invalidate the current cache (if any):
        self._filtered_cache = None

        self.fire_structure_changed()

    #---------------------------------------------------------------------------
    #  Private interface:
    #---------------------------------------------------------------------------

    def _sort_model ( self ):
        """ Sorts the underlying model if that is what the user requested.
        """
        editor = self.editor
        sorted = (editor.factory.sort_model and (self._sorter is not None))
        if sorted:
            items = self.__items( False )[:]
            items.sort( self._sorter )
            if self.reverse ^ self._reverse:
                items.reverse()
            editor.value = items
        return sorted

    def __items ( self, ordered = True ):
        """ Returns the raw list of model objects.
        """
        result = self.editor.value
        if not isinstance( result, SequenceTypes ):
            return [ result ]
        if ordered and self.reverse:
            return ReversedList( result )
        return result

    def __filtered_items ( self ):
        """ Returns the list of all model objects that pass the current filter.
        """
        fc = self._filtered_cache
        if fc is None:
            items  = self.__items()
            filter = self.filter
            if filter is None:
                nitems = [ nitem for nitem in enumerate( items ) ]
                self.filter_summary = 'All %s items' % len( nitems )
            else:
                nitems = [ nitem for nitem in enumerate( items )
                           if filter.filter( nitem[1] ) ]
                self.filter_summary = '%s of %s items' % ( len( nitems ),
                                                           len( items ) )
            sorter = self._sorter
            if sorter is not None:
                nitems.sort( lambda l, r: sorter( l[1], r[1] ) )
                if self._reverse:
                    nitems.reverse()

            self._filtered_map        = [ x[0] for x in nitems ]
            self._filtered_cache = fc = [ x[1] for x in nitems ]
            if self.auto_add_row is not None:
                self._filtered_cache.append( self.auto_add_row )

        return fc

    def __raw_index_of ( self, row ):
        """ Returns the raw index into the underlying model of a specified
            filtered row index.
        """
        if self._filtered_cache is None:
            return row

        return self._filtered_map[ row ]

    def __get_data_column ( self, col ):
        """ Returns a list of model data from the column indexed by *col*.
        """
        column = self.__get_column( col )
        return [ column.get_value( item ) for item in self.__filtered_items() ]

    def __get_columns ( self ):
        columns = self._columns
        if columns is None:
            self._columns = columns = [ c for c in self.editor.columns
                                                if c.visible ]
        return columns

    def __get_column ( self, col ):
        try:
            return self.__get_columns()[ col ]
        except:
            return self.__get_columns()[0]

    def __get_column_name ( self, col ):
        return self.__get_column( col ).name

    def __get_column_formats ( self, col ):
        return None   # Not used/implemented currently

    def _get_column_index_by_trait ( self, name ):
        for i, col in enumerate( self.__get_columns() ):
            if name == col.name:
                return i

#-------------------------------------------------------------------------------
#  'ReversedList' class:
#-------------------------------------------------------------------------------

class ReversedList ( object ):
    """ A list whose order is the reverse of its input.
    """
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, list ):
        self.list = list

    #---------------------------------------------------------------------------
    #  Inserts a value at a specified index in the list:
    #---------------------------------------------------------------------------

    def insert ( self, index, value ):
        """ Inserts a value at a specified index in the list.
        """
        return self.list.insert( self._index( index - 1 ), value )

    #---------------------------------------------------------------------------
    #  Returns the index of the first occurence of the specified value in the
    #  list:
    #---------------------------------------------------------------------------

    def index ( self, value ):
        """ Returns the index of the first occurence of the specified value in
            the list.
        """
        list = self.list[:]
        list.reverse()
        return list.index( value )

    #---------------------------------------------------------------------------
    #  Returns the length of the list:
    #---------------------------------------------------------------------------

    def __len__ ( self ):
        """ Returns the length of the list.
        """
        return len( self.list )

    #---------------------------------------------------------------------------
    #  Returns the value at a specified index in the list:
    #---------------------------------------------------------------------------

    def __getitem__ ( self, index ):
        """ Returns the value at a specified index in the list.
        """
        return self.list[ self._index( index ) ]

    #---------------------------------------------------------------------------
    #  Sets a slice of a list to the contents of a specified sequence:
    #---------------------------------------------------------------------------

    def __setslice__ ( self, i, j, values ):
        """ Sets a slice of a list to the contents of a specified sequence.
        """
        return self.list.__setslice__( self._index( i ), self._index( j ),
                                       values )

    #---------------------------------------------------------------------------
    #  Deletes the item at a specified index:
    #---------------------------------------------------------------------------

    def __delitem__ ( self, index ):
        """ Deletes the item at a specified index.
        """
        return self.list.__delitem__( self._index( index ) )

    #---------------------------------------------------------------------------
    #  Returns the 'reversed' value for a specified index:
    #---------------------------------------------------------------------------

    def _index ( self, index ):
        """ Returns the "reversed" value for a specified index.
        """
        if index < 0:
            return (-1 - index)
        result = (len( self.list ) - index - 1)
        if result >= 0:
            return result
        return index

