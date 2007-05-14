#------------------------------------------------------------------------------
#
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
#  Date:   07/01/2005
#
#------------------------------------------------------------------------------

""" 
Defines the table editor and the table editor factory, for the wxPython user 
interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import true, false, Int, List, Instance, Str, Color, Font, Any, Button, \
           Tuple, Dict, HasPrivateTraits, Trait, Bool, Callable

from enthought.traits.ui.api \
    import View, Item, UI, InstanceEditor, EnumEditor, Handler, SetEditor, \
           ListUndoItem

from enthought.traits.ui.menu \
    import Action, ToolBar, Menu

from enthought.traits.ui.table_column \
    import TableColumn

from enthought.traits.ui.table_filter \
    import TableFilter

from enthought.traits.ui.ui_traits \
    import AView

from enthought.pyface.grid.api \
    import Grid

from enthought.pyface.dock.core \
    import DockWindow, DockSizer, DockSection, DockRegion, DockControl

from enthought.pyface.image_resource \
    import ImageResource

from enthought.util.wx.do_later \
    import do_later

from constants \
    import WindowColor

from editor \
    import Editor

from editor_factory \
    import EditorFactory

from table_model \
    import TableModel, TraitGridSelection

from helper \
    import Orientation

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The filter used to indicate that the user wants to customize the current
# filter
customize_filter = TableFilter( name = 'Customize...' )

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# A trait whose value can be True, False, or a callable function
BoolOrCallable = Trait( False, Bool, Callable )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ wxPython editor factory for table editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # List of initial table column descriptors
    columns = List( TableColumn )

    # List of other table column descriptors (not initially displayed)
    other_columns = List( TableColumn )

    # The object trait containing the list of column descriptors
    columns_name = Str

    # The desired number of visible rows in the table
    rows = Int

    # Initial filter that should be applied to the table
    filter = Instance( TableFilter )

    # List of available filters that can be applied to the table
    filters = List( TableFilter )

    # Filter object used to allow a user to search the table.
    # NOTE: If left as None, the table will not be searchable.
    search = Instance( TableFilter )

    # Default context menu to display when any cell is right-clicked
    menu = Instance( Menu )

    # Are objects deletable from the table?
    deletable = BoolOrCallable( False )

    # Is the table editable?
    editable = true

    # Can the user reorder the items in the table?
    reorderable = false

    # Can the user configure the table columns?
    configurable = true

    # Should the cells of the table automatically size to the optimal size?
    auto_size = true

    # Should a new row automatically be added to the end of the table to allow
    # the user to create new entries? If True, **row_factory** must be set.
    auto_add = false

    # Should the table items be presented in reverse order?
    reverse = false

    # View to use when editing table items.
    # NOTE: If not specified, the table items are not editable in a separate
    # pane of the editor.
    edit_view = AView( ' ' )

    # The handler to apply to **edit_view**
    edit_view_handler = Instance( Handler )

    # Width to use for the edit view
    edit_view_width = Int( -1 )

    # Height to use for the edit view
    edit_view_height = Int( -1 )

    # Layout orientation of the table and its associated editor pane. This
    # attribute applies only if **edit_view** is not ' '.
    orientation = Orientation

    # Is the table sortable by clicking on the column headers?
    sortable = true

    # Does sorting affect the model (vs. just the view)?
    sort_model = false

    # Should grid lines be shown on the table?
    show_lines = true

    # Grid line color
    line_color = Color( 0xC4C0A9 )

    # Show column labels?
    show_column_labels = true

    # Font to use for text in cells
    cell_font = Font

    # Color to use for text in cells
    cell_color = Color( 'black' )

    # Color to use for cell backgrounds
    cell_bg_color = Color( WindowColor )

    # Color to use for read-only cell backgrounds
    cell_read_only_bg_color = Color( 0xF8F7F1 )

    # Font to use for text in labels
    label_font = Font

    # Color to use for text in labels
    label_color = Color( 'black' )

    # Color to use for label backgrounds
    label_bg_color = Color( 0xD7D2BF )

    # Background color of selected item
    selection_bg_color = Color( 0x0D22DF, allow_none = True )

    # Color of selected text
    selection_color = Color( 'white' )

    # Height (in pixels) of column labels
    column_label_height = Int( 25 )

    # Width (in pixels) of row labels
    row_label_width = Int( 82 )

    # The initial height of each row (<= 0 means use default value):
    row_height = Int( 0 )

    # The name of the external '[object.]trait' that the current selection is
    # synced with
    selected = Str

    # Called when a table item is selected
    on_select = Any

    # Called when a table item is double clicked
    on_dclick = Any

    # A factory to generate new rows.
    # NOTE: If None, then the user will not be able to add new rows to the
    # table. If not None, then it must be a callable that accepts
    # **row_factory_args** and **row_factory_kw** and returns a new object
    # that can be added to the table.
    row_factory = Any

    # Arguments to pass to the **row_factory** callable when a new row is
    # created
    row_factory_args = Tuple

    # Keyword arguments to pass to the **row_factory** callable when a new row
    # is created
    row_factory_kw = Dict

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    traits_view = View( [ '{Initial columns}@',
                          Item( 'columns',       resizable = True ),
                          '{Other columns}@',
                          Item( 'other_columns', resizable = True ),
                          '|{Columns}<>' ],
                        [ [ 'deletable{Are items deletable?}', '9',
                            'editable{Are items editable?}',   '9',
                            '-[Item Options]>' ],
                          [ 'show_column_labels{Show column labels?}',      '9',
                            'configurable{Are columns user configurable?}', '9',
                            'auto_size{Should columns auto size?}',
                            '-[Column Options]>' ],
                          [ 'sortable{Are columns sortable?}',
                            Item( 'sort_model{Does sorting affect the model?}',
                                  enabled_when = 'sortable' ),
                            '-[Sorting Options]>' ],
                          [ [ 'show_lines{Show grid lines?}',
                              '|>' ],
                            [ '_', 'line_color{Grid line color}@',
                              '|<>' ],
                            '|[Grid Line Options]' ],
                          '|{Options}' ],
                        [ [ 'cell_color{Text color}@',
                            'cell_bg_color{Background color}@',
                            'cell_read_only_bg_color{Read only color}@',
                            '|[Cell Colors]' ],
                          [ 'cell_font',
                            '|[Cell Font]<>' ],
                          '|{Cell}' ],
                        [ [ 'label_color{Text color}@',
                            'label_bg_color{Background color}@',
                            '|[Label Colors]' ],
                          [ 'label_font@',
                            '|[Label Font]<>' ],
                          '|{Label}' ],
                        [ [ 'selection_color{Text color}@',
                            'selection_bg_color{Background color}@',
                            '|[Selection Colors]' ],
                          '|{Selection}' ],
                        height = 0.5 )

    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------

    def simple_editor ( self, ui, object, name, description, parent ):
        return TableEditor( parent,
                            factory     = self,
                            ui          = ui,
                            object      = object,
                            name        = name,
                            description = description )

    def readonly_editor ( self, ui, object, name, description, parent ):
        self.editable = False
        return TableEditor( parent,
                            factory     = self,
                            ui          = ui,
                            object      = object,
                            name        = name,
                            description = description )

    #---------------------------------------------------------------------------
    #  Event handlers:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the set of filters associated with the editor being changed:
    #---------------------------------------------------------------------------

    def _filters_changed ( self ):
        """ Handles the set of filters associated with the editor being
            changed.
        """
        values = { None: '000:No filter' }
        i      = 0
        for filter in self.filters:
            if not filter.template:
                i += 1
                values[ filter ] = '%03d:%s' % ( i, filter.name )
        values[ customize_filter ] = '%03d:%s' % ( (i + 1),
                                                   customize_filter.name )
        if self._filter_editor is None:
            self._filter_editor = EnumEditor( values = values )
        else:
            self._filter_editor.values = values

    def _filters_items_changed ( self ):
        """ Handles the set of filters associated with the editor being
            changed.
        """
        self._filters_changed()

#-------------------------------------------------------------------------------
#  'TableEditor' class:
#-------------------------------------------------------------------------------

class TableEditor ( Editor ):
    """ Editor that presents data in a table. Optionally, tables can have
    a set of filters that reduce the set of data displayed, according to their
    criteria.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The set of columns currently defined on the editor:
    columns = List( TableColumn )

    # Index of currently edited (i.e., selected) table row
    selected_index = Int

    # The currently selected table row item
    selected = Any

    # Current filter object
    filter = Instance( TableFilter, allow_none = True )

    # The grid widget associated with the editor
    grid = Instance( Grid )

    # The table model associated with the editor
    model = Instance( TableModel )

    # TableEditorToolbar associated with the editor
    toolbar = Any

    # The Traits UI associated with the table editor toolbar
    toolbar_ui = Instance( UI )

    # Is the table editor is scrollable? This value overrides the default.
    scrollable = True

    # Is 'auto_add' mode in effect? (I.e., new rows are automatically added to
    # the end of the table when the user modifies current last row.)
    auto_add = false

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory       = self.factory
        self.filter   = factory.filter
        self.auto_add = (factory.auto_add and (factory.row_factory is not None))
        self.columns  = factory.columns[:]
        self.model    = model = TableModel( editor  = self,
                                            reverse = factory.reverse )
        model.on_trait_change( self._model_sorted, 'sorted', dispatch = 'ui' )
        selected = None
        items    = model.get_filtered_items()
        if factory.editable and (len( items ) > 0):
            selected = items[0]

        if factory.edit_view == ' ':
            self.control = panel = wx.Panel( parent, -1 )
            sizer        = wx.BoxSizer( wx.VERTICAL )
            self._create_toolbar( panel, sizer )

            # Create the table (i.e. grid) control:
            hsizer = wx.BoxSizer( wx.HORIZONTAL )
            hsizer.Add( wx.StaticLine( panel, -1, style = wx.LI_VERTICAL ), 0,
                        wx.EXPAND )
            self._create_grid( panel, hsizer )
            sizer.Add( hsizer, 1, wx.EXPAND )
        else:
            item         = self.item
            name         = item.get_label( self.ui )
            self.control = dw = DockWindow( parent ).control
            panel        = wx.Panel( dw, -1 )
            sizer        = wx.BoxSizer( wx.VERTICAL )
            dc           = DockControl( name    = name + ' Table',
                                        id      = 'table',
                                        control = panel,
                                        style   = 'fixed' )
            contents     = [ DockRegion( contents = [ dc ] ) ]
            self._create_toolbar( panel, sizer )

            selected = None
            items    = model.get_filtered_items()
            if factory.editable and (len( items ) > 0):
                selected = items[0]

            # Create the table (i.e. grid) control:
            hsizer = wx.BoxSizer( wx.HORIZONTAL )
            hsizer.Add( wx.StaticLine( panel, -1, style = wx.LI_VERTICAL ), 0,
                        wx.EXPAND )
            self._create_grid( panel, hsizer )
            sizer.Add( hsizer, 1, wx.EXPAND )

            # Assign the initial object here, so a valid editor will be built
            # when the 'edit_traits' call is made:
            self.selected = selected
            self._ui = ui = self.edit_traits(
                     parent = dw,
                     kind   = 'subpanel',
                     view   = View( [ Item( 'selected@',
                                          editor = InstanceEditor(
                                                       view = factory.edit_view,
                                                       kind = 'subpanel' ),
                                          resizable = True,
                                          width  = factory.edit_view_width,
                                          height = factory.edit_view_height ),
                                      '|<>' ],
                                    resizable = True,
                                    handler   = factory.edit_view_handler ) )

            # Link the ui history of the sub-view into the main view:
            ui.history = self.ui.history

            # Reset the object so that the sub-sub-view will pick up the
            # correct history also:
            self.selected = None
            self.selected = selected

            dc.style = item.dock
            contents.append( DockRegion( contents = [
                                 DockControl( name    = name + ' Editor',
                                              id      = 'editor',
                                              control = ui.control,
                                              style   = item.dock ) ] ) )

            # Finish setting up the DockWindow:
            dw.SetSizer( DockSizer( contents = DockSection(
                          contents = contents,
                          is_row   = (factory.orientation == 'horizontal') ) ) )

        self.sync_value( factory.selected, 'selected' )
        self.sync_value( factory.columns_name, 'columns', 'from',
                         is_list = True )
        self.grid.on_trait_change( self._selection_updated,
                                   'selection_changed', dispatch = 'ui' )

        # Make sure the selection is initialized:
        if len( items ) > 0:
            self.set_selection( items[0] )
        else:
            self._selection_updated( [] )

        # Finish the panel layout setup:
        panel.SetSizer( sizer )

    #---------------------------------------------------------------------------
    #  Creates the associated grid control used to implement the table:
    #---------------------------------------------------------------------------

    def _create_grid ( self, parent, sizer ):
        factory        = self.factory
        selection_mode = 'rows'
        if factory.selection_bg_color is None:
            selection_mode = ''
        self.grid = grid = Grid( parent,
            model                        = self.model,
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
            selection_mode               = selection_mode,
            allow_column_sort            = factory.sortable,
            allow_row_sort               = False,
            column_label_height          = factory.column_label_height,
            row_label_width              = factory.row_label_width )
        _grid = grid._grid
        _grid.AutoSizeRows()
        if factory.rows > 0:
            self.scrollable = False
            dy = (_grid.GetColLabelSize() +
                  (factory.rows * _grid.GetRowSize( 0 )))
            _grid.SetSizeHints( -1, dy, -1, dy )
            sizer.Add( grid.control, 1, wx.EXPAND )
        else:
            _grid.SetSizeHints( -1, 0 )
            sizer.Add( grid.control, 1, wx.EXPAND )
        if factory.row_height > 0:
            _grid.SetDefaultRowSize( factory.row_height )
        return grid.control

    #---------------------------------------------------------------------------
    #  Creates the table editing tool bar:
    #---------------------------------------------------------------------------

    def _create_toolbar ( self, parent, sizer ):
        """ Creates the table editing toolbar.
        """
        factory = self.factory
        toolbar = TableEditorToolbar( parent = parent, editor = self )
        if (toolbar.control is not None) or (len( factory.filters ) > 0):
            tb_sizer = wx.BoxSizer( wx.HORIZONTAL )

            if len( factory.filters ) > 0:
                view = View( [ Item( 'filter<250>{View}',
                                     editor = factory._filter_editor ), '_',
                               Item( 'filter_summary<100>{Results}~',
                                     object = 'model' ), '_',
                               '-' ],
                             resizable = True )
                self.toolbar_ui = ui = view.ui(
                              context = { 'object': self, 'model': self.model },
                              parent  = parent,
                              kind    = 'subpanel' )
                tb_sizer.Add( ui.control, 0 )

            if toolbar.control is not None:
                self.toolbar = toolbar
                tb_sizer.Add( ( 1, 1 ), 1, wx.EXPAND )
                tb_sizer.Add( toolbar.control, 0 )

            sizer.Add( tb_sizer, 0, wx.ALIGN_RIGHT | wx.EXPAND )
            sizer.Add( wx.StaticLine( parent, -1, style = wx.LI_HORIZONTAL ), 0,
                       wx.EXPAND | wx.BOTTOM, 5 )

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( TableEditor, self ).dispose()
        if self.toolbar_ui is not None:
            self.toolbar_ui.dispose()
        if self._ui is not None:
            self._ui.dispose()
        self.grid.on_trait_change( self._selection_updated, 'cell_left_clicked',
                                   remove = True )
        self.model.on_trait_change( self._model_sorted, 'sorted',
                                    remove = True )
        self.grid.dispose()
        self.model.dispose()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        # fixme: Do we need to override this method?
        pass

    #---------------------------------------------------------------------------
    #  Refreshes the editor control:
    #---------------------------------------------------------------------------

    def refresh ( self ):
        """ Refreshes the editor control.
        """
        self.grid._grid.Refresh()

    #---------------------------------------------------------------------------
    #  Sets the current selection to a specified object:
    #---------------------------------------------------------------------------

    def set_selection ( self, *objects ):
        """ Sets the current selection to a specified object.
        """
        self.grid.set_selection( [ TraitGridSelection( obj = object )
                                   for object in objects ] )

    #---------------------------------------------------------------------------
    #  Creates a new row object using the provided factory:
    #---------------------------------------------------------------------------

    def create_new_row ( self ):
        """ Creates a new row object using the provided factory.
        """
        factory = self.factory
        kw      = factory.row_factory_kw.copy()
        if '__table_editor__' in kw:
            kw[ '__table_editor__' ] = self

        return self.ui.evaluate( factory.row_factory,
                                 *factory.row_factory_args, **kw  )

    #---------------------------------------------------------------------------
    #  Adds a specified object as a new row after the specified index:
    #---------------------------------------------------------------------------

    def add_row ( self, object, index = None ):
        """ Adds a specified object as a new row after the specified index.
        """
        if index is None:
            index = self.selected_index
        index, extend = self.model.insert_filtered_item_after( index, object )
        if object in self.model.get_filtered_items():
            self.set_selection( object )
        self._add_undo( ListUndoItem( object = self.object,
                                      name   = self.name,
                                      index  = index,
                                      added  = [ object ] ), extend )

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
        try:
            self.filter = prefs.get( 'filter',  self.filter )

            filters = prefs.get( 'filters', None )
            if filters is not None:
                factory.filters = ([ f for f in factory.filters if f.template ]
                                 + [ f for f in filters if not f.template ])

            columns = prefs.get( 'columns' )
            if columns is not None:
                new_columns = []
                all_columns = self.columns + factory.other_columns
                for column in columns:
                    for column2 in all_columns:
                        if column == column2.get_label():
                            new_columns.append( column2 )
                            break
                self.columns = new_columns

                # Restore the column sizes if possible:
                if not factory.auto_size:
                    widths = prefs.get( 'widths' )
                    if widths is not None:
                        # fixme: Talk to Jason about a better way to do this:
                        self.grid._user_col_size = True

                        set_col_size = self.grid._grid.SetColSize
                        for i, width in enumerate( widths ):
                            if width >= 0:
                                set_col_size( i, width )

            structure = prefs.get( 'structure' )
            if (structure is not None) and (factory.edit_view != ' '):
                self.control.GetSizer().SetStructure( self.control, structure )
        except:
            pass

    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------

    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        get_col_size = self.grid._grid.GetColSize
        result = {
            'filter':    self.filter,
            'filters':   [ f for f in self.factory.filters
                           if not f.template ],
            'columns':   [ c.get_label() for c in self.columns ],
            'widths':    [ get_col_size( i )
                           for i in range( len( self.columns ) ) ]
        }
        if self.factory.edit_view != ' ':
            result[ 'structure' ] = self.control.GetSizer().GetStructure()

        return result

    #---------------------------------------------------------------------------
    #  Event handlers:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the currently selected object being changed:
    #---------------------------------------------------------------------------

    def _selected_changed ( self, selected ):
        """ Handles the currently selected object being changed.
        """
        self.set_selection( selected )

    #---------------------------------------------------------------------------
    #  Handles the user selecting a row in the table when an editor view is
    #  associated with the table:
    #---------------------------------------------------------------------------

    def _selection_updated ( self, event ):
        """ Handles the user selecting a row in the table when an editor view
            is associated with the table.
        """
        toolbar   = self.toolbar
        no_filter = (self.filter is None)
        if len( event ) > 0:
            start, end = event[0][0], event[1][0]
            if start == end:
                self.selected_index = start
                self.selected       = self.model.get_filtered_item( start )
                if toolbar is not None:
                    delete = toolbar.delete
                    n      = len( self.model.get_filtered_items() ) - 1
                    if self.auto_add:
                        n -= 1
                        delete.enabled = (start <= n)
                    else:
                        delete.enabled = True
                    if delete.enabled and callable( self.factory.deletable ):
                        delete.enabled = self.factory.deletable( self.selected )
                    toolbar.search.enabled    = toolbar.add.enabled = True
                    toolbar.move_up.enabled   = (no_filter and (start > 0))
                    toolbar.move_down.enabled = (no_filter and (start < n))

                # Invoke the user 'on_select' handler:
                self.ui.evaluate( self.factory.on_select, self.selected )
                return

        self.selected_index = -1
        if toolbar is not None:
            toolbar.add.enabled     = no_filter
            toolbar.search.enabled  = toolbar.delete.enabled    = \
            toolbar.move_up.enabled = toolbar.move_down.enabled = False

    #---------------------------------------------------------------------------
    #  Handles the contents of the model being resorted:
    #---------------------------------------------------------------------------

    def _model_sorted ( self ):
        """ Handles the contents of the model being resorted.
        """
        self.toolbar.no_sort.enabled = True
        if self.selected is not None:
            do_later( self.set_selection, self.selected )

    #---------------------------------------------------------------------------
    #  Handles the current filter being changed:
    #---------------------------------------------------------------------------

    def _filter_changed ( self, old_filter, new_filter ):
        """ Handles the current filter being changed.
        """
        if new_filter is customize_filter:
            do_later( self._customize_filters, old_filter )
        elif self.model is not None:
            self.model.filter = new_filter
            obj   = self.selected
            items = self.model.get_filtered_items()
            if obj not in items:
                if len( items ) == 0:
                    self.selected_index = -1
                    self.selected       = None
                    self.set_selection()
                    return
                obj = items[0]
            self.set_selection( obj )

    #---------------------------------------------------------------------------
    #  Refresh the list of available filters:
    #---------------------------------------------------------------------------

    def _refresh_filters ( self, filters ):
        factory = self.factory
        # hack: The following line forces the 'filters' to be changed...
        factory.filters = []
        factory.filters = filters

    #---------------------------------------------------------------------------
    #  Allows the user to customize the current set of table filters:
    #---------------------------------------------------------------------------

    def _customize_filters ( self, filter ):
        """ Allows the user to customize the current set of table filters.
        """
        factory = self.factory
        filter_editor = TableFilterEditor( editor = self, filter = filter )
        ui = filter_editor.edit_traits( parent = self.control, view = View(
            [ [ Item( 'filter:filter<200>@',
                      editor    = EnumEditor( values = factory.filters[:],
                                              mode   = 'list' ),
                      resizable = True ),
                '|<>' ],
              [ 'edit:edit', 'new', 'apply', 'delete:delete',
                '|<>' ],
              '-' ],
            title   = 'Customize Filters',
            kind    = 'livemodal',
            height  = .25,
            buttons = [ 'OK', 'Cancel' ],
            #help_id = "enlib|HID_Customize_Filters_Dlg",
        ) )
        if ui.result:
            self._refresh_filters(  ui.info.filter.factory.values )
            self.filter = filter_editor.filter
        else:
            self.filter = filter

    #---------------------------------------------------------------------------
    #  Handles the user requesting that columns not be sorted:
    #---------------------------------------------------------------------------

    def on_no_sort ( self ):
        """ Handles the user requesting that columns not be sorted.
        """
        self.model.no_column_sort()
        self.toolbar.no_sort.enabled = False
        self.set_selection( self.selected )

    #---------------------------------------------------------------------------
    #  Handles the user requesting to move the current item up one row:
    #---------------------------------------------------------------------------

    def on_move_up ( self ):
        """ Handles the user requesting to move the current item up one row.
        """
        # from enthought.debug.fbi import bp; bp()
        index  = self.selected_index - 1
        model  = self.model
        object = model.get_filtered_item( index )
        model.delete_filtered_item_at( index )
        model.insert_filtered_item_after( index, object )
        self.set_selection( model.get_filtered_item( index ) )

    #---------------------------------------------------------------------------
    #  Handles the user requesting to move the current item down one row:
    #---------------------------------------------------------------------------

    def on_move_down ( self ):
        """ Handles the user requesting to move the current item down one row.
        """
        index  = self.selected_index
        model  = self.model
        object = model.get_filtered_item( index )
        model.delete_filtered_item_at( index )
        model.insert_filtered_item_after( index, object )
        self.set_selection( object )

    #---------------------------------------------------------------------------
    #  Handles the user requesting a table search:
    #---------------------------------------------------------------------------

    def on_search ( self ):
        """ Handles the user requesting a table search.
        """
        handler = TableSearchHandler( editor = self )
        search  = self.factory.search
        search.edit_traits( parent  = self.control,
                            context = { 'object':  search,
                                        'handler': handler },
                            view    = 'searchable_view',
                            handler = handler )

    #---------------------------------------------------------------------------
    #  Handles the user requesting to add a new row to the table:
    #---------------------------------------------------------------------------

    def on_add ( self ):
        """ Handles the user requesting to add a new row to the table.
        """
        object = self.create_new_row()
        if object is not None:
            self.add_row( object )

    #---------------------------------------------------------------------------
    #  Handles the user requesting to delete the current row of the table:
    #---------------------------------------------------------------------------

    def on_delete ( self ):
        """ Handles the user requesting to delete the current row of the table.
        """
        selected_index = self.selected_index
        if selected_index >= 0:
            index, object = self.model.delete_filtered_item_at( selected_index )
            self._add_undo( ListUndoItem( object  = self.object,
                                          name    = self.name,
                                          index   = index,
                                          removed = [ object ] ) )
            items = self.model.get_filtered_items()
            if selected_index >= len( items ):
                selected_index -= 1
                if selected_index < 0:
                    self.set_selection()
                    return
            self.set_selection( items[ selected_index ] )

    #---------------------------------------------------------------------------
    #  Handles the user requesting to set the user preference items for the
    #  table:
    #---------------------------------------------------------------------------

    def on_prefs ( self ):
        """ Handles the user requesting to set the user preference items for the
            table.
        """
        columns = self.columns[:]
        columns.extend( [ c
            for c in (self.factory.columns + self.factory.other_columns)
            if c not in columns ] )
        self.edit_traits(
            parent = self.control,
            view   = View( [ Item( 'columns',
                                resizable = True,
                                editor    = SetEditor( values       = columns,
                                                       ordered      = True,
                                                       can_move_all = False ) ),
                             '|<>' ],
                         title     = 'Select and Order Columns',
                         width     = 0.3,
                         height    = 0.3,
                         resizable = True,
                         buttons   = [ 'Undo', 'OK', 'Cancel' ],
                         #help_id  = "enlib|HID_Select_and_Order_Columns_Dlg",
                         kind      = 'livemodal' ) )

    #---------------------------------------------------------------------------
    #  Prepares to have a context menu action called:
    #---------------------------------------------------------------------------

    def prepare_menu ( self, row, column ):
        """ Prepares to have a context menu action called.
        """
        object    = self.model.get_filtered_item( row )
        selection = [ x.obj for x in self.grid.get_selection() ]
        if object not in selection:
            self.set_selection( object )
            selection = [ object ]
        self._menu_context = { 'selection': selection,
                               'object':    object,
                               'column':    column,
                               'editor':    self,
                               'info':      self.ui.info,
                               'handler':   self.ui.handler }

#----- pyface.action 'controller' interface implementation: --------------------

    #---------------------------------------------------------------------------
    #  Adds a menu item to the menu being constructed:
    #---------------------------------------------------------------------------

    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        action = menu_item.item.action
        self.eval_when( action.enabled_when, menu_item, 'enabled' )
        self.eval_when( action.checked_when, menu_item, 'checked' )

    #---------------------------------------------------------------------------
    #  Adds a tool bar item to the tool bar being constructed:
    #---------------------------------------------------------------------------

    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a toolbar item to the toolbar being constructed.
        """
        self.add_to_menu( toolbar_item )

    #---------------------------------------------------------------------------
    #  Returns whether the menu action should be defined in the user interface:
    #---------------------------------------------------------------------------

    def can_add_to_menu ( self, action ):
        """ Returns whether the action should be defined in the user interface.
        """
        if action.defined_when != '':
            try:
                if not eval( action.defined_when, globals(), self._context ):
                    return False
            except:
                from enthought.debug.fbi import if_fbi
                if_fbi()

        if action.visible_when != '':
            try:
                if not eval( action.visible_when, globals(), self._context ):
                    return False
            except:
                from enthought.debug.fbi import if_fbi
                if_fbi()

        return True

    #---------------------------------------------------------------------------
    #  Returns whether the toolbar action should be defined in the user
    #  interface:
    #---------------------------------------------------------------------------

    def can_add_to_toolbar ( self, action ):
        """ Returns whether the toolbar action should be defined in the user
            interface.
        """
        return self.can_add_to_menu( action )

    #---------------------------------------------------------------------------
    #  Performs the action described by a specified Action object:
    #---------------------------------------------------------------------------

    def perform ( self, action ):
        """ Performs the action described by a specified Action object.
        """
        self.ui.do_undoable( self._perform, action )

    def _perform ( self, action ):
        method_name        = action.action
        info               = self.ui.info
        handler            = self.ui.handler
        context            = self._menu_context
        self._menu_context = None
        selection          = context[ 'selection' ]

        if method_name.find( '.' ) >= 0:
            if method_name.find( '(' ) < 0:
                method_name += '()'
            try:
                eval( method_name, globals(), context )
            except:
                # fixme: Should the exception be logged somewhere?
                pass
            return

        method = getattr( handler, method_name, None )
        if method is not None:
            method( info, selection )
            return

        if action.on_perform is not None:
            action.on_perform( selection )
            return

        action.perform( selection )

#-- Menu support methods: ------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Evaluates a condition within a defined context and sets a specified
    #  object trait based on the (assumed) boolean result:
    #---------------------------------------------------------------------------

    def eval_when ( self, condition, object, trait ):
        """ Evaluates a condition within a defined context and sets a specified
        object trait based on the result, which is iassumed to be a Boolean.
        """
        if condition != '':
            value = True
            try:
                if not eval( condition, globals(), self._menu_context ):
                    value = False
            except:
                from enthought.debug.fbi import if_fbi
                if_fbi()
            setattr( object, trait, value )

#-- Private Methods: -----------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Adds an 'undo' item to the undo history (if any):
    #---------------------------------------------------------------------------

    def _add_undo ( self, undo_item, extend = False ):
        history = self.ui.history
        if history is not None:
            history.add( undo_item, extend )

#-------------------------------------------------------------------------------
#  'TableFilterEditor' class:
#-------------------------------------------------------------------------------

class TableFilterEditor ( Handler ):
    """ Editor that manages table filters.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # TableEditor this editor is associated with
    editor = Instance( TableEditor )

    # Current filter
    filter = Instance( TableFilter, allow_none = True )

    # Edit the current filter
    edit = Button

    # Create a new filter and edit it
    new = Button

    # Apply the current filter to the editor's table
    apply = Button

    # Delete the current filter
    delete = Button

    #---------------------------------------------------------------------------
    #  'Handler' interface:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Initializes the controls of a user interface:
    #---------------------------------------------------------------------------

    def init ( self, info ):
        """ Initializes the controls of a user interface.
        """
        # Save both the original filter object reference and its contents:
        if self.filter is None:
            self.filter = info.filter.factory.values[0]
        self._filter = self.filter
        self._filter_copy = self.filter.clone_traits()

    #---------------------------------------------------------------------------
    #  Handles a dialog-based user interface being closed by the user:
    #---------------------------------------------------------------------------

    def closed ( self, info, is_ok ):
        """ Handles a dialog-based user interface being closed by the user.
        """
        if not is_ok:
            # Restore the contents of the original filter:
            self._filter.copy_traits( self._filter_copy )

    #---------------------------------------------------------------------------
    #  Event handlers:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles a new filter being selected:
    #---------------------------------------------------------------------------

    def object_filter_changed ( self, info ):
        """ Handles a new filter being selected.
        """
        filter              = info.object.filter
        info.edit.enabled   = (not filter.template)
        info.delete.enabled = ((not filter.template) and
                               (len( info.filter.factory.values ) > 1))

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'Edit' button:
    #---------------------------------------------------------------------------

    def object_edit_changed ( self, info ):
        """ Handles the user clicking the **Edit** button.
        """
        if info.initialized:
            ui = self.filter.edit( self.editor.model.get_filtered_item( 0 ) )
            if ui.result:
                self._refresh_filters( info )

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'New' button:
    #---------------------------------------------------------------------------

    def object_new_changed ( self, info ):
        """ Handles the user clicking the **New** button.
        """
        if info.initialized:
            # Get list of available filters and find the current filter in it:
            factory = info.filter.factory
            filters = factory.values
            filter  = self.filter
            index   = filters.index( filter ) + 1
            n       = len( filters )
            while (index < n) and filters[ index ].template:
                index += 1

            # Create a new filter based on the current filter:
            new_filter          = filter.clone_traits()
            new_filter.template = False
            new_filter.name     = new_filter._name = 'New filter'

            # Add it to the list of filters:
            filters.insert( index, new_filter )
            self._refresh_filters( info )

            # Set up the new filter as the current filter and edit it:
            self.filter = new_filter
            do_later( self._delayed_edit, info )

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'Apply' button:
    #---------------------------------------------------------------------------

    def object_apply_changed ( self, info ):
        """ Handles the user clicking the **Apply** button.
        """
        if info.initialized:
            self.init( info )
            self.editor._refresh_filters( info.filter.factory.values )
            self.editor.filter = self.filter

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'Delete' button:
    #---------------------------------------------------------------------------

    def object_delete_changed ( self, info ):
        """ Handles the user clicking the **Delete** button.
        """
        # Get the list of available filters:
        filters = info.filter.factory.values

        if info.initialized:
            # Delete the current filter:
            index = filters.index( self.filter )
            del filters[ index ]

            # Select a new filter:
            if index >= len( filters ):
                index -= 1
            self.filter = filters[ index ]
            self._refresh_filters( info )

    #---------------------------------------------------------------------------
    #  Private methods:
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Refresh the filter editor's list of filters:
    #---------------------------------------------------------------------------

    def _refresh_filters ( self, info ):
        """ Refresh the filter editor's list of filters.
        """
        factory = info.filter.factory
        values, factory.values = factory.values, []
        factory.values = values

    #---------------------------------------------------------------------------
    #  Edits the current filter, and deletes it if the user cancels the edit:
    #---------------------------------------------------------------------------

    def _delayed_edit ( self, info ):
        """ Edits the current filter, and deletes it if the user cancels the edit.
        """
        ui = self.filter.edit( self.editor.model.get_filtered_item( 0 ) )
        if not ui.result:
            self.object_delete_changed( info )
        else:
            self._refresh_filters( info )

        # Allow deletion as long as there is more than 1 filter:
        if len( info.filter.factory.values ) > 1:
            info.delete.enabled = True

#-------------------------------------------------------------------------------
#  'TableEditorToolbar' class:
#-------------------------------------------------------------------------------

class TableEditorToolbar ( HasPrivateTraits ):
    """ Toolbar displayed in table editors.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Do not sort columns
    no_sort = Instance( Action,
                        { 'name':    'No Sorting',
                          'tooltip': 'Do not sort columns',
                          'action':  'on_no_sort',
                          'enabled': False,
                          'image':   ImageResource( 'table_no_sort.png' ) } )

    # Move current object up one row
    move_up = Instance( Action,
                        { 'name':    'Move Up',
                          'tooltip': 'Move current item up one row',
                          'action':  'on_move_up',
                          'enabled': False,
                          'image':   ImageResource( 'table_move_up.png' ) } )

    # Move current object down one row
    move_down = Instance( Action,
                          { 'name':    'Move Down',
                            'tooltip': 'Move current item down one row',
                            'action':  'on_move_down',
                            'enabled': False,
                            'image':   ImageResource( 'table_move_down.png' ) })

    # Search the table
    search = Instance( Action,
                       { 'name':    'Search',
                         'tooltip': 'Search table',
                         'action':  'on_search',
                         'image':   ImageResource( 'table_search.png' ) } )

    # Add a row
    add = Instance( Action,
                    { 'name':    'Add',
                      'tooltip': 'Insert new item',
                      'action':  'on_add',
                      'image':   ImageResource( 'table_add.png' ) } )

    # Delete selected row
    delete = Instance( Action,
                       { 'name':    'Delete',
                         'tooltip': 'Delete current item',
                         'action':  'on_delete',
                         'image':   ImageResource( 'table_delete.png' ) } )

    # Edit the user preferences
    prefs = Instance( Action,
                      { 'name':    'Preferences',
                        'tooltip': 'Set user preferences for table',
                        'action':  'on_prefs',
                        'image':   ImageResource( 'table_prefs.png' ) } )

    # The table editor that this is the toolbar for
    editor = Instance( TableEditor )

    # The toolbar control
    control = Any

    #---------------------------------------------------------------------------
    #  Initializes the toolbar for a specified window:
    #---------------------------------------------------------------------------

    def __init__ ( self, parent = None, **traits ):
        super( TableEditorToolbar, self ).__init__( **traits )
        factory = self.editor.factory
        actions = []
        if factory.sortable and (not factory.sort_model):
            actions.append( self.no_sort )
        if factory.reorderable:
            actions.append( self.move_up )
            actions.append( self.move_down )
        if factory.search is not None:
            actions.append( self.search )
        if factory.editable:
            if (factory.row_factory is not None) and (not factory.auto_add):
                actions.append( self.add )
            if factory.deletable != False:
                actions.append( self.delete )
        if factory.configurable:
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
        """ Adds a toolbar item to the too bar being constructed.
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
#  'TableSearchHandler' class:
#-------------------------------------------------------------------------------

class TableSearchHandler ( Handler ):
    """ Handler for saerching a table.
    """
    
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The editor that this handler is associated with
    editor = Instance( TableEditor )

    # Find next matching item
    find_next = Button( 'Find Next' )

    # Find previous matching item
    find_previous = Button( 'Find Previous' )

    # Select all matching items
    select = Button

    # The user is finished searching
    OK = Button( 'Close' )

    # Search status message:
    status = Str

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'Find next' button:
    #---------------------------------------------------------------------------

    def handler_find_next_changed ( self, info ):
        """ Handles the user clicking the **Find** button.
        """
        if info.initialized:
            editor = self.editor
            items  = editor.model.get_filtered_items()
            for i in range( editor.selected_index + 1, len( items ) ):
                if info.object.filter( items[i] ):
                    self.status = 'Item %d matches' % ( i + 1 )
                    editor.set_selection( items[i] )
                    editor.selected_index = i
                    break
            else:
                self.status = 'No more matches found'

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'Find previous' button:
    #---------------------------------------------------------------------------

    def handler_find_previous_changed ( self, info ):
        """ Handles the user clicking the **Find previous** button.
        """
        if info.initialized:
            editor = self.editor
            items  = editor.model.get_filtered_items()
            for i in range( editor.selected_index - 1, -1, -1 ):
                if info.object.filter( items[i] ):
                    self.status = 'Item %d matches' % ( i + 1 )
                    editor.set_selection( items[i] )
                    editor.selected_index = i
                    break
            else:
                self.status = 'No more matches found'

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'Select' button:
    #---------------------------------------------------------------------------

    def handler_select_changed ( self, info ):
        """ Handles the user clicking the **Select** button.
        """
        if info.initialized:
            editor = self.editor
            filter = info.object.filter
            items  = [ item for item in editor.model.get_filtered_items()
                       if filter( item ) ]
            editor.set_selection( *items )
            if len( items ) == 1:
                self.status = '1 item selected'
            else:
                self.status = '%d items selected' % len( items )

    #---------------------------------------------------------------------------
    #  Handles the user clicking 'OK' button:
    #---------------------------------------------------------------------------

    def handler_OK_changed ( self, info ):
        """ Handles the user clicking the OK button.
        """
        if info.initialized:
            info.ui.dispose()

