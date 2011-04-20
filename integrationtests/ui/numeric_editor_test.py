#-------------------------------------------------------------------------------
#
#  NumericEditor test case for Traits UI
#
#  Written by: David C. Morrill
#
#  Date: 11/29/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#  License: BSD Style.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Array, Instance

from traitsui.api \
    import View, Item, HGroup

from traitsui.table_column \
    import NumericColumn

from traitsui.wx.numeric_editor \
    import ToolkitEditorFactory as NumericEditor

from enthought.model.api \
    import ANumericModel, NumericArrayModel, ReductionModel, SelectionModel, \
           NumericItem, ExpressionFilter, IndexFilter

from numpy \
    import array, sin, arange

#-------------------------------------------------------------------------------
#  Defines the numeric editor:
#-------------------------------------------------------------------------------

number_editor = NumericEditor(
    extendable              = True,
    new_columns             = 'last',
    configurable            = True,
    columns                 = [ NumericColumn( name   = 'model_indices',
                                               label  = 'i' ),
                                NumericColumn( name   = 'x',
                                               label  = 'x',
                                               format = '%.2f' ),
                                NumericColumn( name   = 'sinx',
                                               label  = 'sin(x)',
                                               format = '%.3f' ),
                                NumericColumn( name   = 'xsinx',
                                               label  = 'x*sin(x)',
                                               format = '%.3f' ) ],
    other_columns           = [],
    choose_selection_filter = True,
    edit_selection_filter   = True,
    edit_selection_colors   = False,
    selection_filter        = None,
    selection_filter_name   = '',
    user_selection_filter   = IndexFilter(),
    choose_reduction_filter = True,
    edit_reduction_filter   = True,
    reduction_filter        = None,
    reduction_filter_name   = '',
    deletable               = True,
    sortable                = True,
    sort_model              = False,
    editable                = True,
    auto_size               = False,
    show_lines              = True,
    menu                    = None,
    show_column_labels      = True,
    #line_color              = 0xC4C0A9,
    #cell_font              = Font,
    #cell_color              = Color( 'black' )
    #cell_bg_color           = Color( 'white' )
    #cell_read_only_bg_color = Color( 0xF8F7F1 )
    #label_font              = Font
    #label_color             = Color( 'black' )
    #label_bg_color          = Color( 0xD7D2BF )
    #selection_bg_color      = Color( 0x0D22DF )
    #selection_color         = Color( 'white' )
    #column_label_height     = Int( 25 )
    #row_label_width         = Int( 82 )
    #on_select               = Callable
    #on_dclick               = Callable
)

#-------------------------------------------------------------------------------
#  'BunchANumbersApp' class:
#-------------------------------------------------------------------------------

class BunchANumbersApp ( HasPrivateTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    model = Instance( ANumericModel )

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    view = View(
               HGroup( Item( 'model', editor = number_editor,
                                      id     = 'model' ),
#                       Item( 'model', editor = number_editor ),
                       show_labels = False ),
                 title     = 'Numeric Editor Test',
                 id        = 'traitsui.tests.numeric_editor_test',
                 width     = 0.28,
                 height    = 0.6,
                 resizable = True )

#-------------------------------------------------------------------------------
#  Run the test:
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    x     = arange( 0.0, 20.005, 0.1 )
    model = NumericArrayModel( x = x, sinx = sin( x ), xsinx = x * sin( x ) )
    BunchANumbersApp( model = model ).configure_traits()

