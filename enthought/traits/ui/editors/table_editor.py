#------------------------------------------------------------------------------
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
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------
""" Defines the table editor factory for all traits user interface toolkits.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Int, Float, List, Instance, Str, Color, Font, Any, Tuple, Dict, \
            Enum, Trait, Bool, Callable, Range

# CIRCULAR IMPORT FIXME: Importing from the source rather than traits.ui.api
# to avoid circular imports, as this EditorFactory will be part of 
# traits.ui.api as well.     
from enthought.traits.ui.view \
    import View

from enthought.traits.ui.item \
    import Item

from enthought.traits.ui.handler \
    import Handler

from enthought.traits.ui.ui_traits \
    import AView

from enthought.traits.ui.editor_factory \
    import EditorFactory

from enthought.traits.ui.helper \
    import Orientation

from enum_editor import EnumEditor

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# A trait whose value can be True, False, or a callable function
BoolOrCallable = Trait( False, Bool, Callable )

#-------------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
#-------------------------------------------------------------------------------

class ToolkitEditorFactory ( EditorFactory ):
    """ Editor factory for table editors.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # List of initial table column descriptors
    columns = List( Instance('enthought.traits.ui.table_column.TableColumn') )

    # List of other table column descriptors (not initially displayed)
    other_columns = List( 
                     Instance('enthought.traits.ui.table_column.TableColumn') )

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
    filter = Instance( 'enthought.traits.ui.table_filter.TableFilter' )

    # List of available filters that can be applied to the table
    filters = List( Instance( 
                     'enthought.traits.ui.table_filter.TableFilter' ) )

    # Filter object used to allow a user to search the table.
    # NOTE: If left as None, the table will not be searchable.
    search = Instance( 'enthought.traits.ui.table_filter.TableFilter' )

    # Default context menu to display when any cell is right-clicked
    menu = Instance( 'enthought.traits.ui.menu.Menu' )

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
    show_toolbar = Bool( False )

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
    cell_bg_color = Color

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
    #
    # row
    #   Entire rows are selected. At most one row can be selected at once.
    #   This is the default.
    # rows
    #   Entire rows are selected. More than one row can be selected at once.
    # column
    #   Entire columns are selected. At most one column can be selected at
    #   once.
    # columns
    #   Entire columns are selected. More than one column can be selected at
    #   once.
    # cell
    #   Single cells are selected. Only one cell can be selected at once.
    # cells
    #   Single cells are selected. More than one cell can be selected at once.
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
    
    def readonly_editor ( self, ui, object, name, description, parent ):
        """ Generates an "editor" that is read-only.
        Overridden to set the value of the editable trait to False before 
        generating the editor.
        
        """
        self.editable = False
        return super(ToolkitEditorFactory, self).readonly_editor(
                  ui, object, name, description, parent)
    
# Define the TableEditor class
TableEditor = ToolkitEditorFactory

### EOF ---------------------------------------------------------------------
