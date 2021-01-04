# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Instance


# --[Code]---------------------------------------------------------------------
# Shows the incorrect way of defining mutually-referring classes.
try:

    class Chicken(HasTraits):

        # Won't work: 'Egg' not defined yet:
        hatched_from = Instance(Egg)

    class Egg(HasTraits):

        # If we move this class to the top, then this line won't work, because
        # 'Chicken' won't be defined yet:
        created_by = Instance(Chicken)


except NameError as excp:
    print(excp)
