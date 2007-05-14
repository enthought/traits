#------------------------------------------------------------------------------
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   11/28/2005
#
#------------------------------------------------------------------------------
""" Defines the table or grid model used by the numeric editor, based on the
PyFace grid control.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, HasPrivateTraits, Any, Str, Int, List, Instance, Event

from enthought.traits.ui.api \
    import Editor

from enthought.traits.ui.table_column \
    import NumericColumn

from enthought.traits.ui.table_filter \
    import TableFilter

from enthought.traits.ui.ui_traits \
    import SequenceTypes

from enthought.model.api \
    import ANumericModel, SortFilter

from enthought.pyface.grid.api \
    import GridModel, GridSortEvent

from enthought.pyface.grid.trait_grid_cell_adapter \
    import TraitGridCellAdapter

#-------------------------------------------------------------------------------
#  'NumericGridSelection' class:
#-------------------------------------------------------------------------------

class NumericGridSelection ( HasPrivateTraits ):
    """ Structure for holding specification information. """

    # The selected model:
    obj = Instance( ANumericModel )

    # The selected row:
    index = Int( -1 )

    # The selected trait (i.e. column) on the model object:
    name = Str

#-------------------------------------------------------------------------------
#  'NumericEditorModel' class:
#-------------------------------------------------------------------------------

class NumericEditorModel ( GridModel ):
    """ Model used by the NumericEditor.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The editor that created this model
    editor = Instance( Editor )

    # The ANumericModel associated with this view model
    model = Instance( ANumericModel )

    # List of columns that are to be displayed in the table
    columns = List( NumericColumn )

    # List of other table column descriptors (not displayed)
    other_columns = List( NumericColumn )

    # Event fired when the table has been sorted
    sorted = Event

    #---------------------------------------------------------------------------
    #  'object' interface:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, **traits ):
        """ Initializes the object.
        """
        super( NumericEditorModel, self ).__init__( **traits )

        # Set up listeners for any of the model data changing:
        self.model = model = self.editor.model
        model.on_trait_change( self._on_data_changed, 'model_updated',
                               dispatch = 'ui' )
        model.on_trait_change( self._on_data_added,   'model_added',
                               dispatch = 'ui' )

    #---------------------------------------------------------------------------
    #  'NumericEditorModel' interface:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Disposes of the model when it is no longer needed:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the model when it is no longer needed.
        """
        # Remove listeners for any of the model data changing:
        model = self.model
        model.on_trait_change( self._on_data_changed, 'model_updated',
                               remove = True )
        model.on_trait_change( self._on_data_added,   'model_added',
                               remove = True )

    #---------------------------------------------------------------------------
    #  Updates the table view when columns have been changed:
    #---------------------------------------------------------------------------

    def _columns_changed ( self ):
        """ Updates the table view when columns have been changed.
        """
        self._columns = None
        self.fire_structure_changed()

    def _columns_items_changed ( self ):
        self._columns_changed()

    #---------------------------------------------------------------------------
    #  Resets any sorting being performed on the underlying model:
    #---------------------------------------------------------------------------

    def no_column_sort ( self ):
        """ Resets any sorting being performed on the underlying model.
        """
        self.column_sorted = GridSortEvent( index = -1 )

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
        """ Return the size in pixels of the column indexed by *index*.
            A value of -1 or None means to use the default. """
        return self.__get_column( index ).get_width()

    def get_cols_drag_value ( self, cols ):
        """ Returns the value to use when the specified columns are dragged or
            copied and pasted. The parameter *cols* is a list of column indexes.
        """
        return [ self.__get_data_column( col ) for col in cols ]

    def get_cols_selection_value ( self, cols ):
        """ Returns a list of TraitGridSelection objects containing the
            object corresponding to the grid rows and the traits corresponding
            to the specified columns.
        """
        return [ NumericGridSelection( obj  = self.model,
                                       name = self.__get_column_name( col ) )
                 for col in cols ]

    def sort_by_column ( self, col, reverse = False ):
        """ Sorts the model data by the column indexed by *col*.
        """
        # Make sure we allow sorts by column:
        factory = self.editor.factory
        if not factory.sortable:
            return

        # Set up the appropriate sorting filter on the model:
        mode = 'ascending'
        if reverse:
            mode = 'descending'
        self.editor._sort_model.model_filter = SortFilter(
                                         filter = self.__get_column_name( col ),
                                         mode   = mode )

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
        """ Returns the number of rows for this table.
        """
        return len( self.model.model_indices )

    def get_row_name ( self, index ):
        """ Returns the name of the row specified by the (zero-based) *index*.
        """
        return str( self.model.model_indices[ index ] )

    def get_rows_drag_value ( self, rows ):
        """ Return the value to use when the specified rows are dragged or
            copied and pasted. The parameter *rows* is a list of row indexes.
            If there is only one row listed, the method returns the
            corresponding trait object. If more than one row is listed, then it
            returns a list of objects.
        """
        # fixme: Implement a better solution than this...
        return rows

    def get_rows_selection_value ( self, rows ):
        """ Returns a list of NumericGridSelection objects containing the
        objects corresponding to the selected rows.
        """
        return [ NumericGridSelection( obj = self.model, index = row )
                 for row in rows ]

    def is_row_read_only ( self, index ):
        """ Returns True if the row specified by the zero-based *index* is
            read-only.
        """
        return False

    def get_cell_editor ( self, row, col ):
        """ Returns the editor for the specified cell. """

        column = self.__get_column( col )
        editor = column.get_editor( self.model, row )
        if editor is None:
            return None
        # fixme: Implement this (what should we do here?)...
        return None
#        return TraitGridCellAdapter( editor, object, column.name, '',
#                                     context = self.editor.ui.context )

    def get_cell_bg_color ( self, row, col ):
        """ Returns a wxColour object specifying the background color
            of the specified cell. """
        return self.__get_column( col ).get_cell_color( self.model, row )

    def get_cell_text_color ( self, row, col ):
        """ Returns a wxColour object specifying the text color
            of the specified cell. """

        return self.__get_column( col ).get_text_color( self.model, row )

    def get_cell_drag_value ( self, row, col ):
        """ Returns the value to use when the specified cell is dragged or
            copied and pasted.
        """
        return self.__get_column( col ).get_value( self.model, row )

    def get_cell_selection_value ( self, row, col ):
        """ Returns a TraitGridSelection object specifying the data stored
            in the table at (*row&, *col*).
        """
        return NumericGridSelection( obj   = self.model,
                                     index = row,
                                     name  = self.__get_column_name( col ) )

    def resolve_selection ( self, selection_list ):
        """ Returns a list of (row, col) grid-cell coordinates that
            correspond to the objects in *selection_list*. For each coordinate,
            if the row is -1, it indicates that the entire column is selected.
            Likewise coordinates with a column of -1 indicate an entire row
            that is selected. For the NumericEditorModel, the objects in
            *selection_list* must be NumericGridSelection objects.
        """
        cells = []
        index = list( self.model.model_indices ).index
        for selection in selection_list:
            try:
                cells.append( ( index( selection ), -1 ) )
            except:
                pass

        return cells

    def get_cell_context_menu ( self, row, col ):
        """ Returns a Menu object that generates the appropriate context
            menu for this cell.
        """
        menu   = self.__get_column( col ).get_menu( self.model, row )
        editor = self.editor
        if menu is None:
            menu = editor.factory.menu
        if menu is not None:
            editor.prepare_menu( row )
            return ( menu, editor )
        return None

    def get_value ( self, row, col ):
        """ Return the value stored in the table at (*row*, *col*).
        """
        value   = self.get_cell_drag_value( row, col )
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
        Returns True if the value is acceptable, and False otherwise. """
        return self.__get_column( col ).is_droppable( self.model, row, value )


    def is_cell_empty ( self, row, col ):
        """ Returns True if the cell at (*row*, *col*) has a None value, and
            False otherwise.
        """
        return (self.get_value( row, col ) is None)

    def is_cell_read_only ( self, row, col ):
        """ Returns True if the cell at (*row*, *col*) is read-only, and False
            otherwise.
        """
        return (not self.__get_column( col ).is_editable( self.model, row ))

    def get_cell_bg_color ( self, row, col ):
        """ Returns a wxColour object specifying the background color
            of the specified cell.
        """
        return self.__get_column( col ).get_cell_color( self.model, row )

    def get_cell_text_color ( self, row, col ):
        """ Returns a wxColour object specifying the text color of the
            specified cell.
        """
        return self.__get_column( col ).get_text_color( self.model, row )

    def get_cell_font ( self, row, col ):
        """ Returns a wxFont object specifying the font of the specified
            cell.
        """
        return self.__get_column( col ).get_text_font( self.model, row )

    def get_cell_halignment ( self, row, col ):
        """ Returns a string specifying the horizontal alignment of the
            specified cell.

            Returns 'left' for left alignment, 'right' for right alignment,
            or 'center' for center alignment.
        """
        return self.__get_column( col ).get_horizontal_alignment( self.model,
                                                                  row )

    def get_cell_valignment ( self, row, col ):
        """ Returns a string specifying the vertical alignment of the
            specified cell.

            Return 'top' for top alignment, 'bottom' for bottom alignment,
            or 'center' for center alignment.
        """
        return self.__get_column( col ).get_vertical_alignment( self.model,
                                                                row )

    #---------------------------------------------------------------------------
    #  Protected 'GridModel' interface:
    #---------------------------------------------------------------------------

    def _insert_rows ( self, pos, num_rows ):
        """ Inserts *num_rows* at *pos* and fires an event only if a factory
        method for new rows is defined or the model is not empty. Otherwise, it
        returns 0.
        """
        # fixme: Implement this...
        raise NotImplementedError

    def _delete_rows ( self, pos, num_rows ):
        """ Removes rows *pos* through *pos* + *num_rows* from the model.
        """
        # fixme: Implement this...
        raise NotImplementedError

    def _set_value ( self, row, col, value ):
        """ Sets the value of the cell at (*row*, *col*) to *value*.

            Raises a ValueError if the value is vetoed or if the cell at
            (*row*, *col*) does not exist.
        """
        new_rows = 0
        column   = self.__get_column( col )
        try:
            self.model.model_indices[ row ]
        except:
            new_rows = self._insert_rows( self.get_row_count(), 1 )

        column.set_value( self.model, row, value )

        return new_rows

    #---------------------------------------------------------------------------
    #  Trait event handlers:
    #---------------------------------------------------------------------------

    def _on_data_changed ( self, object, name, old, new ):
        """ Forces the grid to refresh when the underlying list changes.
        """
        self.fire_structure_changed()
        self.editor.model_changed()

    def _on_data_added ( self, event ):
        """ Forces the grid to refresh when data is added to the underlying list.
        """
        pass  # fixme: Implement this...

    #---------------------------------------------------------------------------
    #  Private interface:
    #---------------------------------------------------------------------------

    def __get_data_column ( self, col ):
        """ Returns a list of model data from the column indexed by *col*.
        """
        return self.__get_column( col ).get_data_column( self.model )

    def __get_columns ( self ):
        columns = self._columns
        if columns is None:
            self._columns = columns = [ c for c in self.columns if c.visible ]
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

