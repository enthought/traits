#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

#--(View Default Button Changes)------------------------------------------------
"""
View Default Button Changes
===========================

For the last year or so, use of the following **View** traits for managing the
default buttons displayed at the bottom of a view has been deprecated:

- apply
- revert
- undo
- ok
- cancel

Use of these traits has been supplanted by use of the *buttons* trait instead.

As part of the ongoing phasing out of these traits, the following changes have
been implemented in Traits 3.0:

- All use of the *apply*, *revert*, *undo*, *ok* and *cancel* traits have been
  removed from views contained within the traits package itself, and have been
  replaced with the *buttons* trait.

- The default value for each of the deprecated traits has been changed from
  **True** to **False**.

While use of the deprecated **View** traits is still allowed at the moment, the
affect of these changes could cause changes in behavior within existing code
that has not yet removed references to the deprecated traits.

In particular, the most likely side effect is for some or all of the default
**View** buttons to disappear from views which are implicitly relying on the
default values for each of the deprecated traits. Views which explicitly set
the deprecated **View** traits or use the newer *buttons* trait should not be
affected.

The correct fix for any **View** which has buttons disappear after installing
Traits 3.0 is to add a *buttons* trait with the correct value set to the
**View**.

Note that in a future release, the deprecated view traits will actually be
removed from the **View** class.
"""

#--<Imports>--------------------------------------------------------------------

from traits.api import *
from traitsui.api import *

#--[Adder Class]----------------------------------------------------------------

# Click the run button to view the pop-up dialog...

class Adder ( HasTraits ):

    value_1 = Float
    value_2 = Float
    sum     = Property( depends_on = [ 'value_1', 'value_2' ] )

    view = View(
        Item( 'value_1' ),
        Item( 'value_2' ),
        '_',
        Item( 'sum', style = 'readonly' ),
        title   = 'Adding Machine',
        buttons = [ 'OK' ]
    )

    def _get_sum ( self ):
        return (self.value_1 + self.value_2)

#--<Example>--------------------------------------------------------------------

popup = Adder()

