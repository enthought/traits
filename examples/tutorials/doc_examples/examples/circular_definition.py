#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.


#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Instance


#--[Code]----------------------------------------------------------------------
# Shows the incorrect way of defining mutually-referring classes.
try:
    class Chicken(HasTraits):

        # Won't work: 'Egg' not defined yet:
        hatched_from = Instance(Egg)

    class Egg(HasTraits):

        # If we move this class to the top, then this line won't work, because
        # 'Chicken' won't be defined yet:
        created_by = Instance(Chicken)

except NameError, excp:
    print excp
