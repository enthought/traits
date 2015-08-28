#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

from traits.api    import *
from traitsui.api import *

class Team ( HasTraits ):

    batting_order = List( Str )
    roster        = List( [ 'Tom', 'Dick', 'Harry', 'Sally' ], Str )

    view = View( Item( 'batting_order', editor = SetEditor( name    = 'roster',
                                                            ordered = True ) ),
                 '_', 'roster@',
                 height=500,
                 resizable=True)

if __name__ == '__main__':
    Team().configure_traits()
