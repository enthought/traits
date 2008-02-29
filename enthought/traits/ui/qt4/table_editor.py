#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the table editor and the table editor factory, for the PyQt user 
    interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

from enthought.traits.api \
    import Int, Float, List, Instance, Str, Color, Font, Any, Tuple, Dict, \
            Enum, Trait, Bool, Callable, Range

from enthought.traits.ui.api \
    import View, Item, EnumEditor, Handler

from enthought.traits.ui.menu \
    import Menu

from enthought.traits.ui.table_column \
    import TableColumn

from enthought.traits.ui.table_filter \
    import TableFilter

from enthought.traits.ui.ui_traits \
    import AView

from constants \
    import WindowColor

from editor \
    import Editor

from editor_factory \
    import EditorFactory

from table_model \
    import TableModel

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
    """ PyQt editor factory for table editors.
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

    # The optional extended name of the trait used to specify an external filter
    # for the table data. The value of the trait must either be an instance of
    # TableEditor, a callable that accepts one argument (a table row) and 
    # returns True or False to indicate whether the specified object passes the
    # filter or not, or **None** to indicate that no filter is to be applied:
    filter_name = Str

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
    editable = Bool( True )

    # Should the editor become active after the first click
    edit_on_first_click = Bool( True )

    # Can the user reorder the items in the table?
    reorderable = Bool( False )

    # Can the user configure the table columns?
    configurable = Bool( True )

    # Should the cells of the table automatically size to the optimal size?
    auto_size = Bool( True )

    # Should a new row automatically be added to the end of the table to allow
    # the user to create new entries? If True, **row_factory** must be set.
    auto_add = Bool( False )

    # Should the table items be presented in reverse order?
    reverse = Bool( False )

    # The DockWindow graphical theme:
    dock_theme = Any

    # View to use when editing table items.
    # NOTE: If not specified, the table items are not editable in a separate
    # pane of the editor.
    edit_view = AView( ' ' )

    # The handler to apply to **edit_view**
    edit_view_handler = Instance( Handler )

    # Width to use for the edit view
    edit_view_width = Float( -1.0 )

    # Height to use for the edit view
    edit_view_height = Float( -1.0 )

    # Layout orientation of the table and its associated editor pane. This
    # attribute applies only if **edit_view** is not ' '.
    orientation = Orientation

    # Is the table sortable by clicking on the column headers?
    sortable = Bool( True )

    # Does sorting affect the model (vs. just the view)?
    sort_model = Bool( False )

    # Should grid lines be shown on the table?
    show_lines = Bool( True )

    # Should the toolbar be displayed? (Note that False will override settings
    # such as 'configurable', etc., and is a quick way to prevent the toolbar
    # from being displayed; but True will not cause a toolbar to appear if one 
    # would not otherwise have been displayed)
    show_toolbar = Bool( True )

    # The vertical scroll increment for the table:
    scroll_dy = Range( 1, 32 )

    # Grid line color
    line_color = Color( 0xC4C0A9 )

    # Show column labels?
    show_column_labels = Bool( True )

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

    # The theme to use for normal cells:
    cell_theme = Any

    # The theme to use for alternate row cells (defaults to 'cell_theme):
    alt_theme = Any

    # The theme to use for selected cells:
    selected_theme = Any

    # Color of selected text
    selection_color = Color( 'white' )

    # Height (in pixels) of column labels
    column_label_height = Int( 25 )

    # Width (in pixels) of row labels
    row_label_width = Int( 82 )

    # The initial height of each row (<= 0 means use default value):
    row_height = Int( 0 )

    # The optional extended name of the trait that the indices of the items 
    # currently passing the table filter are synced with:
    filtered_indices = Str

    # The selection mode of the table. The meaning of the various values are as
    # follows:
    # - row:     Entire rows are selected. At most one row can be selected at 
    #            once. This is the default.
    # - rows:    Entire rows are selected. More than one row can be selected at 
    #            once.
    # - column:  Entire columns are selected. At most one column can be selected
    #            at once.
    # - columns: Entire columns are selected. More than one column can be 
    #            selected at once.
    # - cell:    Single cells are selected. Only one cell can be selected at 
    #            once.
    # - cells:   Single cells are selected. More than one cell can be selected 
    #            at once.
    selection_mode = Enum( 'row', 'rows', 'column', 'columns', 'cell', 'cells' )

    # The optional extended name of the trait that the current selection is
    # synced with:
    selected = Str

    # The optional extended trait name of the trait that the indices of the
    # current selection are synced with:
    selected_indices = Str

    # The optional extended trait name of the trait that should be assigned
    # an ( object, column ) tuple when a table cell is clicked on (Note: If you
    # want to receive repeated clicks on the same cell, make sure the trait is 
    # defined as an Event):
    click = Str

    # The optional extended trait name of the trait that should be assigned
    # an ( object, column ) tuple when a table cell is double-clicked on
    # (Note: if you want to receive repeated double-clicks on the same cell, 
    # make sure the trait is defined as an Event):
    dclick = Str

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

class TableEditor(Editor):
    """ Editor that presents data in a table. Optionally, tables can have
        a set of filters that reduce the set of data displayed, according to 
        their criteria.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The set of columns currently defined on the editor:
    columns = List(TableColumn)

    # The table model associated with the editor:
    model = Instance(TableModel)

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget."""

        factory = self.factory
        self.columns = factory.columns[:]
        self.model = TableModel(editor=self)
        self.control = _TableView(editor=self)

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor."""

        pass

#-------------------------------------------------------------------------------
#  '_TableView' class:
#-------------------------------------------------------------------------------

class _TableView(QtGui.QTableView):
    """A QTableView configured to behave as expected by TraitsUI."""

    def __init__(self, editor):
        """Initialise the object."""

        QtGui.QTableView.__init__(self)

        self._editor = editor

        self.setModel(self._editor.model)
        self.verticalHeader().hide()

        if self._editor.factory.auto_size:
            self.horizontalHeader().setStretchLastSection(True)
            self.resizeColumnsToContents()

    def sizeHint(self):
        """Reimplemented to support auto_size."""

        sh = QtGui.QTableView.sizeHint(self)

        if self._editor.factory.auto_size:
            w = 0

            for colnr in range(len(self._editor.columns)):
                w += self.sizeHintForColumn(colnr)

            sh.setWidth(w)

        return sh
