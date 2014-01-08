#-------------------------------------------------------------------------------
#
#  TableEditor test case for Traits UI which tests editing of lists instead of
#  editing of objects.
#
#  Written by: David C. Morrill
#
#  Date: 07/06/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasStrictTraits, List

from traitsui.api \
    import View, Item, TableEditor

from traitsui.table_column \
    import ListColumn

from traitsui.table_filter \
    import TableFilter

#-------------------------------------------------------------------------------
#  Sample data:
#-------------------------------------------------------------------------------

people = [
   [ 'Dave',   39, '555-1212' ],
   [ 'Mike',   28, '555-3526' ],
   [ 'Joe',    34, '555-6943' ],
   [ 'Tom',    22, '555-7586' ],
   [ 'Dick',   63, '555-3895' ],
   [ 'Harry',  46, '555-3285' ],
   [ 'Sally',  43, '555-8797' ],
   [ 'Fields', 31, '555-3547' ]
]

#-------------------------------------------------------------------------------
#  Table editor definition:
#-------------------------------------------------------------------------------

table_editor = TableEditor(
    columns            = [ ListColumn( index = 0, label = 'Name'  ),
                           ListColumn( index = 1, label = 'Age'   ),
                           ListColumn( index = 2, label = 'Phone' ) ],
    editable           = False,
    show_column_labels = True,       #
)

#-------------------------------------------------------------------------------
#  'TableTest' class:
#-------------------------------------------------------------------------------

class TableTest ( HasStrictTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    people = List

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    traits_view = View( [ Item( 'people',
                                editor    = table_editor,
                                resizable = True ),
                          '|[]<>' ],
                        title   = 'Table Editor Test',
                        width   = .17,
                        height  = .23,
                        buttons = [ 'OK', 'Cancel' ],
                        kind    = 'live' )

#-------------------------------------------------------------------------------
#  Run the tests:
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    tt = TableTest( people = people )
    tt.configure_traits()
    for p in tt.people:
        print p
        print '--------------'
