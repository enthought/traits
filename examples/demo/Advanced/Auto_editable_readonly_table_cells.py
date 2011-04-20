#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
This example shows how to define a read-only, auto-edit table column using a
custom pop-up view.

The example displays a list of integer values from 1 to n, where 'n' can be set
using the slider at the top of the view. Each entry in the list shows the value
of the integer and the number of unique factors it has.

Mousing over the number of factors for a particular integer displays a pop-up
list containing the unique factors for the integer. Mousing out of the cell
causes the pop-up list to be removed (and perhaps causes a new pop-up list to
be displayed, depending upon whether the mouse entered a new cell or not).

Creating the auto pop-up effect is achieved by setting the 'auto_editable' trait
of the associated ObjectColumn to True and also specifying a view to display
on mouse over as the value of the ObjectColumn's 'view' trait.

Note that this style of auto pop-up view can only be used with non-editable
table editor fields. If the field is editable, then setting 'auto_editable' to
True will cause the editor associated with the ObjectColumn to be automatically
activated on mouse over, rather than the pop-up view specified by the 'view'
trait.
"""

#-- Imports --------------------------------------------------------------------

from traits.api \
    import HasTraits, Int, List, Range, Property, property_depends_on

from traitsui.api \
    import View, VGroup, Item, TableEditor

from traitsui.table_column \
    import ObjectColumn

#-- Integer Class --------------------------------------------------------------

class Integer ( HasTraits ):

    # The value:
    n = Int

#-- Factor Class ---------------------------------------------------------------

class Factor ( HasTraits ):

    # The number being factored:
    n = Int

    # The list of factors of 'n':
    factors = Property( List )

    @property_depends_on( 'n' )
    def _get_factors ( self ):
        n      = self.n
        i      = 1
        result = []

        while (i * i) <= n:
            j = n / i
            if (i * j) == n:
                result.append( Integer( n = i ) )
                if i != j:
                    result.append( Integer( n = j ) )
            i += 1

        result.sort( lambda l, r: cmp( l.n, r.n ) )

        return result

#-- The table editor used for the pop-up view ----------------------------------

factor_table_editor = TableEditor(
    columns = [
        ObjectColumn( name                 = 'n',
                      width                = 1.0,
                      editable             = False,
                      horizontal_alignment = 'center' )
    ],
    sortable           = False,
    auto_size          = False,
    show_toolbar       = False,
    show_column_labels = False
)

#-- The table editor used for the main view ------------------------------------

factors_view = View(
    Item( 'factors',
          id         = 'factors',
          show_label = False,
          editor     = factor_table_editor
    ),
    id     = 'traits.examples.demo.Advanced.factors_view',
    kind   = 'info',
    height = 0.30,
)

factors_table_editor = TableEditor(
    columns = [
        ObjectColumn( name                 = 'n',
                      width                = 0.5,
                      editable             = False,
                      horizontal_alignment = 'center' ),
        ObjectColumn( name                 = 'factors',
                      width                = 0.5,
                      editable             = False,
                      horizontal_alignment = 'center',
                      auto_editable        = True,
                      format_func          = lambda f: '%s factors' % len( f ),
                      view                 = factors_view ),
    ],
    sortable     = False,
    auto_size    = False,
    show_toolbar = False
)

#-- Factors Class --------------------------------------------------------------

class Factors ( HasTraits ):

    # The maximum number to include in the table:
    max_n = Range( 1, 1000, 20, mode = 'slider' )

    # The list of Factor objects:
    factors = Property( List )

    # The view of the list of Factor objects:
    view = View(
        VGroup(
            VGroup(
                Item( 'max_n' ),
                show_labels = False,
                show_border = True,
                label       = 'Maximum Number'
            ),
            VGroup(
                Item( 'factors',
                      show_label = False,
                      editor     = factors_table_editor
                ),
            )
        ),
        title     = 'List of numbers and their factors',
        width     = 0.2,
        height    = 0.4,
        resizable = True
    )

    @property_depends_on( 'max_n' )
    def _get_factors ( self ):
        return [ Factor( n = i + 1 ) for i in xrange( self.max_n ) ]

#-- Create and run the demo ----------------------------------------------------

# Create the demo:
demo = Factors()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

