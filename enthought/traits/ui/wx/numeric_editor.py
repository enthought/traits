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
# Date:   11/15/2005
#
#  Symbols defined: ToolkitEditorFactory
#
#------------------------------------------------------------------------------
""" Defines the NumericModel editor and editor factory, for the wxPython user
interface toolkit.
.
"""
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.util.numerix \
    import compress

from enthought.traits.api \
    import HasPrivateTraits, List, Enum, Str, Instance, Int, Any, Callable, \
           Color, RGBAColor, Font, Bool, Expression, Property, true, false

from enthought.traits.ui.api \
    import View, VGroup, Item, SetEditor, TableEditor, EnumEditor

from enthought.traits.ui.menu \
    import Menu, Action, ToolBar

from enthought.traits.ui.table_column \
    import NumericColumn, ObjectColumn

from enthought.util.wx.do_later \
    import do_later

from enthought.pyface.grid.api \
    import Grid

from enthought.pyface.sizers.flow \
    import FlowSizer

from enthought.pyface.image_resource \
    import ImageResource

from enthought.model.api \
    import ANumericModel, NumericFilter, IndexFilter, ExpressionFilter, \
           MappingModel, CachedModel, FilterSet, EvaluatedNumericItem

from enthought.model.numeric_editor \
    import NumericFilterEditor

from numeric_editor_model \
    import NumericEditorModel

from constants \
    import WindowColor

from editor \
    import Editor

from basic_editor_factory \
    import BasicEditorFactory

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Default cell color of a new synthetic column
SyntheticColor = ( 1.0, 1.0, 0.792, 1.0 )

# List of column traits to be copied as part of the user preferences
column_traits = [
    'label', 'format', 'text_color', 'text_font', 'cell_color',
    'read_only_cell_color', 'selected_text_color', 'selected_text_font',
    'selected_cell_color', 'horizontal_alignment', 'vertical_alignment', 'width'
]

valid_python_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
digits             = '0123456789'

#-------------------------------------------------------------------------------
#  Converts an RGBA color to a wx.Colour:
#-------------------------------------------------------------------------------

def RGBA_to_WX ( color ):
    """ Converts an RGBA color to a wx.Colour.
    """
    return wx.Colour( int( 255 * color[0] ),
                      int( 255 * color[1] ),
                      int( 255 * color[2] ) )

#-------------------------------------------------------------------------------
#  'NumericEditor' class:
#-------------------------------------------------------------------------------

class NumericEditor ( Editor ):
    """ Editor for a NumericModel.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Is the numeric editor scrollable? This value overrides the default.
    scrollable = True

    # Index of the currently edited (i.e., selected) table row
    selected = Int

    # The ANumericModel associated with the editor
    model = Instance( ANumericModel )

    # The grid widget associated with the editor
    grid = Instance( Grid )

    # The table model associated with the editor
    grid_model = Instance( NumericEditorModel )

    # NumericEditorToolbar associated with the editor
    toolbar = Any

    # List of synthetic columns
    synthetic = List

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        model   = self.value

        # For efficiency reasons, make sure we are using a caching model:
        if not isinstance( model, CachedModel ):
            model = CachedModel( model )
        self.model = model

        # Add the user selection to the model (if required):
        user_selection_filter = factory.user_selection_filter
        if user_selection_filter is not None:
            self._user_model              = model.get_selection_model()
            self._user_model.model_filter = user_selection_filter.clone_traits()

        # Add the user deletion to the model (if required):
        if factory.editable and factory.deletable:
            self._deletion_model              = model.get_reduction_model()
            self._deletion_model.model_filter = IndexFilter( invert = True )

        # Initialize the current selection:
        self._selection = []
        self._external_selection = []

        # Set up the list of synthetic columns:
        self.synthetic = []

        # Set up the grid model:
        if (len( factory.columns ) + len( factory.other_columns )) == 0:
            columns = [ NumericColumn(
                             name       = item.name,
                             label      = item.label or item.name,
                             format     = item.format,
                             cell_color = RGBA_to_WX( item.background_color_ ),
                             text_color = RGBA_to_WX( item.foreground_color_ ) )
                        for item in model.model_items ]
        else:
            columns = factory.columns[:]

        self.grid_model = grid_model = \
            NumericEditorModel( editor        = self,
                                columns       = columns,
                                other_columns = factory.other_columns[:] )
        grid_model.on_trait_change( self._model_sorted, 'sorted',
                                    dispatch = 'ui' )
        self.control = panel = wx.Panel( parent, -1 )
        sizer        = wx.BoxSizer( wx.VERTICAL )
        self._create_toolbar( panel, sizer )

        # Create the table (i.e. grid) control:
        table = self._create_grid( panel, sizer )

        self.grid.on_trait_change( self._selection_updated,
                                   'selection_changed', dispatch = 'ui' )

        # Set up to handle sorting (if required):
        if factory.sortable:
            if factory.sort_model:
                self._sort_model = model.get_mapping_model()
            else:
                self._sort_model = MappingModel( model )
                self.model.insert_model( self._sort_model )

        # Listen for new columns being added to the model:
        model.on_trait_change( self._columns_added, 'model_added',
                               dispatch = 'ui' )

        # Finish the panel layout setup:
        panel.SetSizer( sizer )

    #---------------------------------------------------------------------------
    #  Creates the associated grid control used to implement the table:
    #---------------------------------------------------------------------------

    def _create_grid ( self, parent, sizer ):
        """ Creates the grid control used to implement the table.
        """
        factory   = self.factory
        self.grid = grid = Grid( parent,
            model                        = self.grid_model,
            enable_lines                 = factory.show_lines,
            grid_line_color              = factory.line_color,
            show_row_headers             = False,
            show_column_headers          = factory.show_column_labels,
            default_cell_font            = factory.cell_font,
            default_cell_text_color      = factory.cell_color,
            default_cell_bg_color        = factory.cell_bg_color,
            default_cell_read_only_color = factory.cell_read_only_bg_color,
            default_label_font           = factory.label_font,
            default_label_text_color     = factory.label_color,
            default_label_bg_color       = factory.label_bg_color,
            selection_bg_color           = factory.selection_bg_color,
            selection_text_color         = factory.selection_color,
            autosize                     = factory.auto_size,
            read_only                    = not factory.editable,
            selection_mode               = 'rows',
            allow_column_sort            = factory.sortable,
            allow_row_sort               = False,
            edit_on_first_click          = factory.editable,
            column_label_height          = factory.column_label_height,
            row_label_width              = factory.row_label_width )
        grid._grid.AutoSizeRows()
        sizer.Add( grid.control, 1, wx.EXPAND )
        return grid.control

    #---------------------------------------------------------------------------
    #  Creates the table editing tool bar:
    #---------------------------------------------------------------------------

    def _create_toolbar ( self, parent, sizer ):
        """ Creates the table-editing toolbar.
        """
        model   = self.model
        factory = self.factory
        toolbar = NumericEditorToolbar( parent = parent, editor = self )
        if ((toolbar.control is not None)    or
             factory.choose_selection_filter or
             factory.edit_selection_filter   or
             factory.choose_reduction_filter or
             factory.edit_reduction_filter):
            tb_sizer = FlowSizer( wx.HORIZONTAL )

            if factory.choose_reduction_filter or factory.edit_reduction_filter:
                self._reduction_model  = model.get_reduction_model()
                self._reduction_filter = self._get_filter(
                       factory.reduction_filter, factory.reduction_filter_name )
                self._reduction_view, self._reduction_ui = \
                    self._create_filter_view( parent, tb_sizer,
                        self._reduction_filter, self._reduction_model,
                        factory.edit_reduction_filter, 'Filter' )

            if factory.choose_selection_filter or factory.edit_selection_filter:
                self._selection_model  = model.get_selection_model()
                self._selection_filter = self._get_filter(
                       factory.selection_filter, factory.selection_filter_name )
                self._selection_view, self._selection_ui = \
                    self._create_filter_view( parent, tb_sizer,
                        self._selection_filter, self._selection_model,
                        factory.edit_selection_filter, 'Select' )

            if toolbar.control is not None:
                self.toolbar = toolbar
                tb_sizer.Add( ( 1, 1 ), 1, wx.EXPAND )
                tb_sizer.Add( toolbar.control, 0 )

            sizer.Add( tb_sizer, 0, wx.ALIGN_RIGHT | wx.EXPAND )
            sizer.Add( wx.StaticLine( parent, -1, style = wx.LI_HORIZONTAL ), 0,
                       wx.EXPAND | wx.BOTTOM, 5 )

    #---------------------------------------------------------------------------
    #  Gets the appropriate filter object:
    #---------------------------------------------------------------------------

    def _get_filter ( self, filter, filter_name ):
        """ Gets the appropriate filter object.
        """
        if filter is not None:
            return filter
        if filter_name != '':
            return numeric_filter( self.editor.ui, filter_name )
        return new_filter_set()

    #---------------------------------------------------------------------------
    #  Creates the filter view for a specified filter:
    #---------------------------------------------------------------------------

    def _create_filter_view ( self, parent, sizer, filter_set, model, editable,
                                    label ):
        """ Creates the filter view for a specified filter.
        """
        filter_view = NumericFilterView( model      = model,
                                         parent     = parent,
                                         editable   = editable ).set(
                                         filter_set = filter_set )
        view = View( [ Item( 'filter<140>{%s}' % label,
                             editor = EnumEditor( name = 'filters' ) ),
                       '_', '-' ],
                     resizable = True )
        ui = filter_view.edit_traits( parent = parent,
                                      view   = view,
                                      kind   = 'subpanel' )
        sizer.Add( ui.control, 0 )
        return ( filter_view, ui )

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( NumericEditor, self ).dispose()

        if self._selection_ui is not None:
            self._selection_ui.dispose()

        if self._reduction_ui is not None:
            self._reduction_ui.dispose()

        self.grid.on_trait_change( self._selection_updated, 'cell_left_clicked',
                                   remove = True )
        self.grid_model.on_trait_change( self._model_sorted, 'sorted',
                                         remove = True )
        self.grid_model.dispose()

        # Remove all models that the editor added:
        model = self.model
        model.remove_model( self._reduction_model )
        model.remove_model( self._selection_model )
        model.remove_model( self._user_selection_model )
        model.remove_model( self._deletion_model )
        model.remove_model( self._sort_model )

        # Remove event listeners from the model:
        model.on_trait_change( self._columns_added, 'model_added',
                               remove = True )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass

#-- UI preference save/restore interface ---------------------------------------

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the
    #  editor:
    #---------------------------------------------------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        factory = self.factory

        # Restore the reduction filters:
        if self._reduction_model is not None:
            filter = prefs.get( 'reduction_filter' )
            if ((filter is not None) and
                (factory.reduction_filter is None) and
                (factory.reduction_filter_name == '')):
                self._reduction_filter = filter
                if self._reduction_view is not None:
                    self._reduction_view.filter_set = filter

            filter = prefs.get( 'current_reduction_filter' )
            if filter is not None:
                self._reduction_model.model_filter = filter
                if self._reduction_view is not None:
                    self._reduction_view.filter = filter

        # Restore the selection filter:
        if self._selection_model is not None:
            filter = prefs.get( 'selection_filter' )
            if ((filter is not None) and
                (factory.selection_filter is None) and
                (factory.selection_filter_name == '')):
                self._selection_filter = filter
                if self._selection_view is not None:
                    self._selection_view.filter_set = filter

            filter = prefs.get( 'current_selection_filter' )
            if filter is not None:
                self._selection_model.model_filter = filter
                if self._selection_view is not None:
                    self._selection_view.filter = filter

        # Restore the table columns:
        columns = prefs.get( 'columns' )
        if columns is not None:
            all_columns = factory.columns + factory.other_columns
            grid_model  = self.grid_model
            grid_model.columns = self._restore_columns( columns, all_columns )
            grid_model.other_columns = self._restore_columns(
                                               prefs.get( 'other_columns', [] ),
                                               all_columns )
            grid_model.other_columns += all_columns
            if not factory.auto_size:
                set_col_size = self.grid._grid.SetColSize
                for i, column in enumerate( grid_model.columns ):
                    if column.width >= 0:
                        set_col_size( i, column.width )

        # Restore any synthetic columns:
        if factory.extendable:
            synthetic_columns = prefs.get( 'synthetic' )
            if synthetic_columns is not None:
                self.synthetic = synthetic_columns
                self.model.model_base.model_items.extend( [
                    EvaluatedNumericItem( name     = synthetic.name,
                                          evaluate = synthetic.evaluate )
                    for synthetic in synthetic_columns ] )

    #---------------------------------------------------------------------------
    #  Restores a list of user preference columns:
    #---------------------------------------------------------------------------

    def _restore_columns ( self, columns, all_columns ):
        """ Restores a list of user preference columns.
        """
        new_columns = []
        for column in columns:
            if column._is_synthetic:
                new_columns.append( column )
                self.toolbar.delete_synthetic.enabled = True
            else:
                label = column.get_label()
                for i, column2 in enumerate( all_columns ):
                    if label == column2.get_label():
                        column2.copy_traits( column, column_traits )
                        new_columns.append( column2 )
                        del all_columns[i]
                        break

        return new_columns

    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------

    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        factory = self.factory

        # Save the current set of columns:
        get_col_size = self.grid._grid.GetColSize
        prefs = { 'columns': [ c.set( width = get_col_size( i ) ) for i, c in
                               enumerate( self.grid_model.columns ) ],
                  'other_columns': self.grid_model.other_columns[:] }

        # Save the reduction model related data (if any):
        if self._reduction_model is not None:
            prefs[ 'current_reduction_filter' ] = \
                self._reduction_model.model_filter
            if factory.reduction_filter is None:
                if factory.reduction_filter_name != '':
                    numeric_filter( self.editor.ui,
                                    factory.reduction_filter_name,
                                    self._reduction_filter )
                else:
                    prefs[ 'reduction_filter' ] = self._reduction_filter

        # Save the selection model related data (if any):
        if self._selection_model is not None:
            prefs[ 'current_selection_filter' ] = \
                self._selection_model.model_filter
            if factory.selection_filter is None:
                if factory.selection_filter_name != '':
                    numeric_filter( self.editor.ui,
                                    factory.selection_filter_name,
                                    self._selection_filter )
                else:
                    prefs[ 'selection_filter' ] = self._selection_filter

        # Save any synthetic columns that were added:
        if len( self.synthetic ) > 0:
            prefs[ 'synthetic' ] = self.synthetic[:]

        return prefs

    #---------------------------------------------------------------------------
    #  Event handlers:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the contents of the model being changed:
    #---------------------------------------------------------------------------

    def model_changed ( self ):
        """ Handles the contents of the model being changed.
        """
        if self.factory.auto_select:
            model_selection = self.model.model_selection
            if model_selection is None:
                self._external_selection = []
            else:
                self._external_selection = list( compress( model_selection,
                                          self.model.model_indices, axis = 0 ) )
            self._check_selection_status()

    #---------------------------------------------------------------------------
    #  Handles columns being added to the model:
    #---------------------------------------------------------------------------

    def _columns_added ( self, items ):
        """ Handles columns being added to the model.
        """
        grid_columns = self.grid_model.columns
        names        = [ column.name for column in grid_columns ]
        columns      = []
        for item in items:
            if not item.name in names:
                column = NumericColumn(
                           name          = item.name,
                           label         = item.label or item.name,
                           format        = item.format,
                           cell_color    = RGBA_to_WX( item.background_color_ ),
                           text_color    = RGBA_to_WX( item.foreground_color_ ),
                           _is_synthetic = True )
                if isinstance( item, EvaluatedNumericItem ):
                    self.toolbar.delete_synthetic.enabled = True
                columns.append( column )

        if len( columns ) > 0:
            if self.factory.new_columns == 'first':
                grid_columns[ 0: 0 ] = columns
            else:
                grid_columns.extend( columns )

    #---------------------------------------------------------------------------
    #  Handles the user selecting a row in the table when an editor view is
    #  associated with the table:
    #---------------------------------------------------------------------------

    def _selection_updated ( self, event ):
        """ Handles the user selecting a row in the table when an editor view
            is associated with the table.
        """
        # Guard against recursion:
        if self._recursive:
            return
        self._recursive = True

        selection = self._selection
        if len( event ) == 0:
            if len( selection ) > 0:
                del selection[:]
                self.grid.set_selection( [] )
        else:
            selection.extend( self.model.model_indices[ event[0][0]:
                                                        event[1][0] + 1 ] )
            selection.sort()

        if self._user_model is not None:
            # fix me: This hack to fix problems with numeric->numpy conversion
            self._user_model.model_filter.indices = [int(x) for x in selection]

        self._check_selection_status()

        # Release recursion lock:
        self._recursive = False

    #---------------------------------------------------------------------------
    #  Handles the contents of the model being resorted:
    #---------------------------------------------------------------------------

    def _model_sorted ( self ):
        """ Handles the contents of the model being resorted.
        """
        self.toolbar.no_sort.enabled = True

    #---------------------------------------------------------------------------
    #  Handles the user requesting that columns not be sorted:
    #---------------------------------------------------------------------------

    def on_no_sort ( self ):
        """ Handles the user requesting that columns not be sorted.
        """
        self.grid_model.no_column_sort()
        self._sort_model.model_filter = None
        self.toolbar.no_sort.enabled  = False

    #---------------------------------------------------------------------------
    #  Handles the user requesting to delete the current selection from the
    #  table:
    #---------------------------------------------------------------------------

    def on_delete ( self ):
        """ Handles the user requesting to delete the current selection from
            the table.
        """
        self._deletion_model.model_filter.indices.extend(
                                    self._selection + self._external_selection )
        del self._selection[:]
        del self._external_selection[:]
        self.toolbar.undelete.enabled = True
        self.grid.set_selection( [] )

    #---------------------------------------------------------------------------
    #  Handles the user requesting to undelete all deleted rows from the table:
    #---------------------------------------------------------------------------

    def on_undelete ( self ):
        """ Handles the user requesting to undelete all deleted rows from the
            table.
        """
        selection = self._deletion_model.model_filter.indices[:]
        del self._deletion_model.model_filter.indices[:]
        self.grid.set_selection( selection )
        self.toolbar.undelete.enabled = False

    #---------------------------------------------------------------------------
    #  Handles the user requesting to create an evaluated column:
    #---------------------------------------------------------------------------

    def on_synthetic ( self ):
        """ Handles the user requesting to create an evaluated column.
        """
        synthetic = SyntheticColumn()
        if synthetic.edit_traits( parent = self.ui.control ).result:
            self.synthetic.append( synthetic )
            self.model.model_base.model_items.append(
                        EvaluatedNumericItem(
                            name             = synthetic.name,
                            label            = synthetic.label,
                            evaluate         = synthetic.evaluate,
                            foreground_color = synthetic.foreground_color,
                            background_color = synthetic.background_color ) )

    #---------------------------------------------------------------------------
    #  Handles the user requesting to delete an evaluated column:
    #---------------------------------------------------------------------------

    def on_delete_synthetic ( self ):
        """ Handles the user requesting to delete an evaluated  column.
        """
        sd = SyntheticColumnDeleter( synthetic     = self.synthetic[:],
                                     all_synthetic = self.synthetic[:] )
        if sd.edit_traits( parent = self.ui.control ).result:
            columns = self.grid_model.columns
            for item in self.synthetic:
                if item not in sd.synthetic:
                    name = item.name
                    for i, column in enumerate( columns ):
                        if name == column.name:
                            del columns[i]
                            break
            self.synthetic = sd.synthetic

    #---------------------------------------------------------------------------
    #  Handles the user requesting to edit the current selection colors:
    #---------------------------------------------------------------------------

    def on_colors ( self ):
        """ Handles the user requesting to edit the current selection colors.
        """
        pass  # fixme: Implement this...

    #---------------------------------------------------------------------------
    #  Handles the user requesting to set the column display preference items
    #  for the table:
    #---------------------------------------------------------------------------

    def on_display_prefs ( self ):
        """ Handles the user requesting to set the column display preference
            items for the table.
        """
        grid_model = self.grid_model
        grid_model.edit_traits(
            view = View( [ Item( 'columns', id     = 'columns',
                                            editor = columns_table_editor ),
                           '|<>' ],
                         id        = 'enthought.traits.ui.wx.numeric_editor.display_columns',
                         title     = 'Edit column properties',
                         width     = 0.7,
                         height    = 0.3,
                         resizable = True,
                         buttons   = [ 'OK' ],
                         kind      = 'livemodal' ) )
        grid_model.columns = grid_model.columns[:]
        self.grid._grid.Refresh()

    #---------------------------------------------------------------------------
    #  Handles the user requesting to set the user preference items for the
    #  table:
    #---------------------------------------------------------------------------

    def on_prefs ( self ):
        """ Handles the user requesting to set the user preference items for the
            table.
        """
        grid_model = self.grid_model
        values     = grid_model.columns + grid_model.other_columns
        grid_model.edit_traits(
            view = View( [ Item( 'columns',
                                 editor = SetEditor(
                                              values       = values,
                                              ordered      = True,
                                              can_move_all = False ) ),
                           '|<>' ],
                         title     = 'Select and Order Columns',
                         width     = 0.3,
                         height    = 0.3,
                         resizable = True,
                         buttons   = [ 'Undo', 'OK', 'Cancel' ],
                         kind      = 'livemodal' ) )

        columns                  = grid_model.columns
        grid_model.other_columns = [ c for c in values if c not in columns ]

    #---------------------------------------------------------------------------
    #  Prepares to have a context menu action called:
    #---------------------------------------------------------------------------

    def prepare_menu ( self, row ):
        """ Prepares to have a context menu action called.
        """
        pass  # fixme: Implement this...
#        object    = self.model.get_filtered_item( row )
#        selection = [ x.obj for x in self.grid.get_selection() ]
#        if object not in selection:
#            self.set_selection( object )
#            selection = [ object ]
#        self._menu_context = { 'selection': selection,
#                               'editor':    self,
#                               'info':      self.ui.info,
#                               'handler':   self.ui.handler }

#-- Private Methods: -----------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Makes sure all selection related toolbar icons are in the right state:
    #---------------------------------------------------------------------------

    def _check_selection_status ( self ):
        """ Makes sure all selection related toolbar icons are in the right
            state.
        """
        toolbar = self.toolbar
        if toolbar is not None:
            toolbar.delete.enabled = ((len( self._selection ) +
                                       len( self._external_selection )) > 0)

    #---------------------------------------------------------------------------
    #  Adds an 'undo' item to the undo history (if any):
    #---------------------------------------------------------------------------

    def _add_undo ( self, undo_item, extend = False ):
        """ Adds an undo item to the undo history (if any).
        """
        history = self.ui.history
        if history is not None:
            history.add( undo_item, extend )

#-------------------------------------------------------------------------------
#  'NumericEditorToolbar' class:
#-------------------------------------------------------------------------------

class NumericEditorToolbar ( HasPrivateTraits ):
    """ A toolbar for a numeric editor. The toolbar items defined in this class
    are:

    * No sort: Returns the table to an unsorted state.
    * Delete: Deletes the item in the selected row.
    * Undelete: Restores all deleted items.
    * Evaluated column: Adds an evaluated column to the table.
    * Delete evaluated column: Deletes an evaluated column from the table.
    * Selection colors: Sets selection colors for the table.
    * Display preferences: Opens a dialog box so the user can set
      preferences about the display of the table.
    * Column preferences: Opens a dialog box so the user can set the order
      of the columns.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Do not sort columns:
    no_sort = Instance( Action,
                        { 'name':    'No sort',
                          'tooltip': 'Do not sort columns',
                          'action':  'on_no_sort',
                          'enabled': False,
                          'image':   ImageResource( 'table_no_sort.png' ) } )

    # Delete action:
    delete = Instance( Action,
                       { 'name':    'Delete',
                         'tooltip': 'Delete current item',
                         'action':  'on_delete',
                         'enabled': False,
                         'image':   ImageResource( 'table_delete.png' ) } )

    # Undelete action:
    undelete = Instance( Action,
                         { 'name':    'Undelete',
                           'tooltip': 'Restores all deleted items',
                           'action':  'on_undelete',
                           'enabled': False,
                           'image':   ImageResource( 'table_undelete.png' ) } )

    # Add a synthetic column to the model:
    synthetic = Instance( Action,
                          { 'name':    'Evaluated column',
                            'tooltip': 'Add an evaluated column to the table',
                            'action':  'on_synthetic',
                            'image':   ImageResource( 'table_synthetic.png' ) } )

    # Delete a synthetic column from the model:
    delete_synthetic = Instance( Action,
                          { 'name':    'Delete evaluated column',
                            'tooltip': 'Delete an evaluated column from the table',
                            'action':  'on_delete_synthetic',
                            'enabled': False,
                            'image':   ImageResource( 'table_delete_synthetic.png' ) } )

    # Edit the selection colors:
    colors = Instance( Action,
                       { 'name':    'Selection colors',
                         'tooltip': 'Set selection colors for table',
                         'action':  'on_colors',
                         'image':   ImageResource( 'table_colors.png' ) } )

    # Edit the column display preferences action:
    display = Instance( Action,
                      { 'name':    'Display Preferences',
                        'tooltip': 'Set column display preferences for table',
                        'action':  'on_display_prefs',
                        'image':   ImageResource( 'table_display.png' ) } )

    # Edit the user column ordering/visibility preferences action:
    prefs = Instance( Action,
                      { 'name':    'Column Preferences',
                        'tooltip': 'Set column ordering preferences for table',
                        'action':  'on_prefs',
                        'image':   ImageResource( 'table_prefs.png' ) } )

    # The table editor this is the toolbar for:
    editor = Instance( NumericEditor )

    # The toolbar control:
    control = Any

    #---------------------------------------------------------------------------
    #  Initializes the toolbar for a specified window:
    #---------------------------------------------------------------------------

    def __init__ ( self, parent = None, **traits ):
        super( NumericEditorToolbar, self ).__init__( **traits )
        factory = self.editor.factory
        actions = []

        if factory.sortable:
            actions.append( self.no_sort )

        if factory.editable and factory.deletable:
            actions.append( self.undelete )
            actions.append( self.delete )

        if factory.extendable:
            actions.append( self.synthetic )
            actions.append( self.delete_synthetic )

        if (factory.choose_selection_filter or
            factory.edit_selection_filter) and factory.edit_selection_colors:
            actions.append( self.colors )

        if factory.configurable:
            actions.append( self.display )
            actions.append( self.prefs )

        if len( actions ) > 0:
            toolbar = ToolBar( image_size      = ( 16, 16 ),
                               show_tool_names = False,
                               show_divider    = False,
                               *actions )
            self.control = toolbar.create_tool_bar( parent, self )

            # fixme: Why do we have to explictly set the size of the toolbar?
            #        Is there some method that needs to be called to do the
            #        layout?
            self.control.SetSize( wx.Size( 23 * len( actions ), 16 ) )

    #---------------------------------------------------------------------------
    #  PyFace/Traits menu/toolbar controller interface:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Adds a menu item to the menu bar being constructed:
    #---------------------------------------------------------------------------

    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        pass

    #---------------------------------------------------------------------------
    #  Adds a tool bar item to the tool bar being constructed:
    #---------------------------------------------------------------------------

    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a toolbar item to the toolbar being constructed.
        """
        pass

    #---------------------------------------------------------------------------
    #  Returns whether the menu action should be defined in the user interface:
    #---------------------------------------------------------------------------

    def can_add_to_menu ( self, action ):
        """ Returns whether the action should be defined in the user interface.
        """
        return True

    #---------------------------------------------------------------------------
    #  Returns whether the toolbar action should be defined in the user
    #  interface:
    #---------------------------------------------------------------------------

    def can_add_to_toolbar ( self, action ):
        """ Returns whether the toolbar action should be defined in the user
            interface.
        """
        return True

    #---------------------------------------------------------------------------
    #  Performs the action described by a specified Action object:
    #---------------------------------------------------------------------------

    def perform ( self, action ):
        """ Performs the action described by a specified Action object.
        """
        getattr( self.editor, action.action )()

#-------------------------------------------------------------------------------
#  'NamedSingleton' class:
#-------------------------------------------------------------------------------

class NamedSingleton ( HasPrivateTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    name = Str

    #---------------------------------------------------------------------------
    #  Returns the string representation of the object:
    #---------------------------------------------------------------------------

    def __str__ ( self ):
        return self.name

NoneFilter      = NamedSingleton( name = 'None' )
CustomizeFilter = NamedSingleton( name = 'Customize...' )

#-------------------------------------------------------------------------------
#  'NumericFilterView' class:
#-------------------------------------------------------------------------------

class NumericFilterView ( HasPrivateTraits ):
    """ Displays a set of filters for a NumericModel editor.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Model this editor is associated with
    model = Instance( ANumericModel )

    # Parent window for pop-up filter editor
    parent = Instance( wx.Window )

    # Current filter set
    filter_set = Instance( FilterSet )

    # List of currently selectable filters
    filters = List

    # Currently selected filter
    filter = Any

    # A top_level filter selected by the user
    selected_filter = Any

    # Are the filters editable?
    editable = Bool

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    view = View(
        VGroup(
            Item( 'filter_set',
                  id     = 'filter_set',
                  editor = NumericFilterEditor().set(
                               on_select = 'object._filter_selected' ) ),
            show_labels = False
        ),
        id        = 'enthought.traits.ui.wx.numeric_editor.filter_editor',
        width     = 0.35,
        height    = 0.4,
        resizable = True,
        buttons   = [ 'OK' ]
    )

    #---------------------------------------------------------------------------
    #  Handles the 'filter_set' trait being changed:
    #---------------------------------------------------------------------------

    def _filter_set_changed ( self, old, new ):
        """ Handles the **filter_set** trait being changed.
        """
        if old is not None:
            old.on_trait_change( self._init_filters, 'filters',
                                 remove = True )
            old.on_trait_change( self._init_filters, 'filters_items',
                                 remove = True )
        if new is not None:
            new.on_trait_change( self._init_filters, 'filters',
                                 dispatch = 'ui' )
            new.on_trait_change( self._init_filters, 'filters_items',
                                 dispatch = 'ui' )

        self._init_filters()
        if self.model.model_filter is None:
            self.filter = NoneFilter

    #---------------------------------------------------------------------------
    #  Initializes the list of filters available for selection:
    #---------------------------------------------------------------------------

    def _init_filters ( self ):
        """ Initializes the list of filters available for selection.
        """
        filters = [ NoneFilter ] + self.filter_set.filters
        if self.editable:
            filters.append( CustomizeFilter )
        self.filters = filters

    #---------------------------------------------------------------------------
    #  Handles a new filter being selected:
    #---------------------------------------------------------------------------

    def _filter_changed ( self, old, new ):
        """ Handles a new filter being selected.
        """
        if new is not CustomizeFilter:
            if new is NoneFilter:
                new = None
            self.model.model_filter = new
        else:
            do_later( self.set, filter = old )
            do_later( self._edit_filters )

    #---------------------------------------------------------------------------
    #  Displays the filter editing dialog:
    #---------------------------------------------------------------------------

    def _edit_filters ( self ):
        """ Displays the filter editor dialog box.
        """
        self.selected_filter = None
        self.edit_traits( parent = self.parent, kind = 'livemodal' )
        self.filters = []
        self._init_filters()
        if self.selected_filter is not None:
            self.filter = self.selected_filter

    #---------------------------------------------------------------------------
    #  Handles a new filter item being selected:
    #---------------------------------------------------------------------------

    def _filter_selected ( self, filter ):
        """ Handles a new filter item being selected.
        """
        if filter in self.filter_set.filters:
            self.selected_filter = filter

#-------------------------------------------------------------------------------
#  'SyntheticColumn'
#-------------------------------------------------------------------------------

class SyntheticColumn ( HasPrivateTraits ):
    """ A column for a NumericModel editor, whose values are results of
    evaluating an expression.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Name of the synthetic column
    name = Property

    # Label of the synthetic column
    label = Property

    # String formatting rule
    format = Str( '%.3f' )

    # Evaluation code for the synthetic value
    evaluate = Expression

    # Foreground color
    foreground_color = RGBAColor( 'black' )

    # Background_color
    background_color = RGBAColor( SyntheticColor )

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    view = View( 'evaluate', 'name', 'label', '_',
                 'format', 'foreground_color', 'background_color',
                 id        = 'enthought.traits.ui.wx.numeric_editor.synthetic_column',
                 title     = 'Define evaluated column',
                 kind      = 'livemodal',
                 resizable = True,
                 buttons   = [ 'OK', 'Cancel' ] )

    #---------------------------------------------------------------------------
    #  Implementation of the 'label' property:
    #---------------------------------------------------------------------------

    def _get_label ( self ):
        if self._label:
            return self._label
        return self.evaluate

    def _set_label ( self, value ):
        old = self.label
        if value != old:
            self._label = value
            self.trait_property_changed( 'label', old, value )

    #---------------------------------------------------------------------------
    #  Implementation of the 'name' property:
    #---------------------------------------------------------------------------

    def _get_name ( self ):
        if self._name:
            return self._name
        result = ''
        for c in self.evaluate:
            if ((c in valid_python_chars) or
                ((result != '') and (c in digits))):
                result += c
        return result

    def _set_name ( self, value ):
        old = self.name
        if value != old:
            self._name = value
            self.trait_property_changed( 'name', old, value )

    #---------------------------------------------------------------------------
    #  Handles the 'evaluate' trait being changed:
    #---------------------------------------------------------------------------

    def _evaluate_changed ( self ):
        if not self._label:
            self.trait_property_changed( 'label', self._label, self.label )

        if not self._name:
            self.trait_property_changed( 'name', self._name, self.name )

    #---------------------------------------------------------------------------
    #  Returns the string represention of the object:
    #---------------------------------------------------------------------------

    def __str__ ( self ):
        """ Returns the string represention of the object.
        """
        return self.label

#-------------------------------------------------------------------------------
#  'SyntheticColumnDeleter' class:
#-------------------------------------------------------------------------------

class SyntheticColumnDeleter ( HasPrivateTraits ):
    """ Handles deleting SyntheticColumn objects.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # List of synthetic columns
    synthetic = List

    # Master list of synthetic columns
    all_synthetic = List

    #---------------------------------------------------------------------------
    #  Trait view definitions:
    #---------------------------------------------------------------------------

    view = View( Item( 'synthetic{}',
                       editor = SetEditor(
                                  name               = 'all_synthetic',
                                  left_column_title  = 'Columns to be deleted:',
                                  right_column_title = 'Columns to keep:' ) ),
                 id        = 'enthought.traits.ui.wx.numeric_editor.delete_synthetic_editor',
                 title     = 'Delete evaluated columns',
                 resizable = True,
                 width     = 0.20,
                 height    = 0.25,
                 kind      = 'livemodal',
                 buttons   = [ 'OK', 'Cancel' ] )

#-------------------------------------------------------------------------------
#  'ColorColumn' class:
#-------------------------------------------------------------------------------

class ColorColumn ( ObjectColumn ):

    #---------------------------------------------------------------------------
    #  Gets the value of the column for a specified object:
    #---------------------------------------------------------------------------

    def get_value ( self, object ):
        """ Gets the value of the column for a specified object.
        """
        return ''

    #---------------------------------------------------------------------------
    #  Returns the cell background color for the column for a specified object:
    #---------------------------------------------------------------------------

    def get_cell_color ( self, object ):
        """ Returns the cell background color for the column for a specified
            object.
        """
        return getattr( object, self.name + '_' )

#-------------------------------------------------------------------------------
#  'FontColumn' class:
#-------------------------------------------------------------------------------

class FontColumn ( ObjectColumn ):

    #---------------------------------------------------------------------------
    #  Returns the text font for the column for a specified object:
    #---------------------------------------------------------------------------

    def get_text_font ( self, object ):
        """ Returns the text font for the column for a specified object.
        """
        return getattr( object, self.name )

#-------------------------------------------------------------------------------
#  NumericEditor 'columns' table editor:
#-------------------------------------------------------------------------------

columns_table_editor = TableEditor(
    editable = True,
    columns  = [ ObjectColumn( name  = 'label' ),
                 ObjectColumn( name  = 'format' ),
                 ObjectColumn( name  = 'horizontal_alignment',
                               label = 'Horizontal' ),
                 ObjectColumn( name  = 'vertical_alignment',
                               label = 'Vertical' ),
                 ColorColumn(  name  = 'text_color',
                               label = 'Text' ),
                 ColorColumn(  name  = 'cell_color',
                               label = 'Cell' ),
                 ColorColumn(  name  = 'read_only_cell_color',
                               label = 'Read Only' ),
                 FontColumn(   name  = 'text_font',
                               label = 'Font' ),
                 ColorColumn(  name  = 'selected_text_color',
                               label = 'Selected Text' ),
                 ColorColumn(  name  = 'selected_cell_color',
                               label = 'Selected Cell' ),
                 FontColumn(   name  = 'selected_text_font',
                               label = 'Selected Font' ),
               ]
)

#-------------------------------------------------------------------------------
#  Get/Set a named filter stored in the Traits UI database:
#-------------------------------------------------------------------------------

numeric_filters = {}

def numeric_filter ( ui, name, filter = None ):
    """ Gets or sets a named filter stored in the Traits UI database.
    """
    global numeric_filters

    if filter is None:
        filter = numeric_filters.get( name )
        if filter is None:
            db = ui.get_ui_db()
            if db is not None:
                filter = db.get( '$$NumericFilter$$' + name )
                db.close()
            if filter is None:
                filter = new_filter_set()
    else:
        db = ui.get_ui_db( mode = 'c' )
        if db is not None:
            db[ '$$NumericFilter$$' + name ] = filter
            db.close()

    numeric_filters[ name ] = filter

    return filter

#-------------------------------------------------------------------------------
#  Makes a new filter set:
#-------------------------------------------------------------------------------

def new_filter_set ( ):
    """ Makes a new filter set.
    """
    return FilterSet( name    = 'Filter set',
                      filters = [ ExpressionFilter(
                                      name   = 'Select all',
                                      filter = 'model_indices >= 0' ) ] )

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( BasicEditorFactory ):
    """ wxPython editor factory for NumericModel editors.
    """
    #---------------------------------------------------------------------------
    # Trait definitions:
    #---------------------------------------------------------------------------

    # The class of the editor to always be created:
    klass = NumericEditor

    # Should an external selection be automatically selected in the editor?
    auto_select = true

    # Can the user add new columns to the model?
    extendable = true

    # Where should new columns be added
    new_columns = Enum( 'last', [ 'first', 'last' ] )

    # Can the user configure the table columns?
    configurable = true

    # List of initial table column descriptors
    columns = List( NumericColumn )

    # List of other table column descriptors (not initially displayed)
    other_columns = List( NumericColumn )

    # Can the user choose the selection filter?
    choose_selection_filter = true

    # Can the user edit the selection filter?
    edit_selection_filter = true

    # Can the user edit the selection colors?
    edit_selection_colors = true

    # The filter to use for selecting model data. This trait is mutually
    # exclusive with **selection_filter_name**.
    selection_filter = Instance( NumericFilter )

    # The name of the filter to use for selecting model data. This trait is
    # mutually exclusive with **selection_filter**.
    selection_filter_name = Str

    # The MaskFilter to use for injecting the current user selection into
    # the model pipeline
    user_selection_filter = Instance( IndexFilter )

    # Can the user choose the reduction filter?
    choose_reduction_filter = true

    # Can the user edit the reduction filter?
    edit_reduction_filter = true

    # The filter to use for reducing the model data. This trait is mutually
    # exclusive with **reduction_filter_name**.
    reduction_filter = Instance( NumericFilter )

    # The name of the filter to use for reducing model data. This trait is
    # mutually exclusive with **reduction_filter**.
    reduction_filter_name = Str

    # Are rows deletable from the table?
    deletable = false

    # Can the user sort the data?
    sortable = false

    # Does sorting affect the model?
    sort_model = false

    # Is the table editable?
    editable = true

    # Should the cells of the table automatically size to the optimal size?
    auto_size = false

    # Should grid lines be shown on the table?
    show_lines = true

    # Default context menu to display when any cell is right_clicked
    menu = Instance( Menu )

    # Grid line color
    line_color = Color( 0xC4C0A9 )

    # Should column labels be displayed?
    show_column_labels = true

    # The default font to use for text in cells
    cell_font = Font

    # The default color to use for text in cells
    cell_color = Color( 'black' )

    # The default color to use for cell backgrounds
    cell_bg_color = Color( WindowColor )

    # The default color to use for read-only cell backgrounds
    cell_read_only_bg_color = Color( 0xF8F7F1 )

    # The default font to use for text in labels
    label_font = Font

    # The default color to use for text in labels
    label_color = Color( 'black' )

    # The default color to use for label backgrounds
    label_bg_color = Color( 0xD7D2BF )

    # The default background color for selections
    selection_bg_color = Color( 0x0D22DF )

    # The default text color for selections
    selection_color = Color( 'white' )

    # Height (in pixels) of column labels
    column_label_height = Int( 25 )

    # Width (in pixels) of row labels
    row_label_width = Int( 82 )

    # Called when a table item is selected
    on_select = Callable

    # Called when a table item is double-clicked
    on_dclick = Callable

