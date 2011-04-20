#-------------------------------------------------------------------------------
#
#  TableEditor test case for Traits UI
#
#  Written by: David C. Morrill
#
#  Date: 07/05/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#  License: BSD Style.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasTraits, List

from traitsui.api \
    import View, Item, TableEditor

from traitsui.wx.color_column \
    import ColorColumn

from enthought.enable.api \
    import ColorTrait

class Thingy ( HasTraits ):
    color = ColorTrait( 'black' )

#-------------------------------------------------------------------------------
#  Sample data:
#-------------------------------------------------------------------------------

colors = [
   Thingy( color = 'red'),
   Thingy( color = 'orange'),
   Thingy( color = 'yellow'),
   Thingy( color = 'green'),
   Thingy( color = 'blue'),
   Thingy( color = 'indigo'),
   Thingy( color = 'violet'),
   Thingy( color = 'black'),
   Thingy( color = 'white'),
]

class TableTest ( HasTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    colors = List( Thingy )

    table_editor = TableEditor(
        columns            = [ ColorColumn( name = 'color' ),
                             ],

        editable           = True,
        deletable          = True,
        sortable           = True,        #
        sort_model         = True,
        show_lines         = True,        #
        orientation        = 'vertical',
        show_column_labels = True,        #
        row_factory        = Thingy
    )


    traits_view = View(
        [ Item( 'colors',
                id     = 'colors',
                editor = table_editor ),
          '|[]<>' ],
        title     = 'Table Editor Test',
        id        = 'traitsui.tests.table_editor_color_test',
        dock      = 'horizontal',
        width     = .4,
        height    = .3,
        resizable = True,
        kind      = 'live' )

#-------------------------------------------------------------------------------
#  Run the tests:
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    tt = TableTest( colors = colors )
    tt.configure_traits()
