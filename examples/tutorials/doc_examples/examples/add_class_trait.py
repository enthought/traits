# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# add_class_trait.py --- Example of mutually-referring classes
#                        using add_class_trait()


# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Instance


# --[Code]---------------------------------------------------------------------
# Defining mutually-referring classes using add_class_trait()
class Chicken(HasTraits):
    pass


class Egg(HasTraits):
    created_by = Instance(Chicken)


# Now that 'Egg' is defined, we can add the 'hatched_from' trait to
# solve the mutual-reference problem...

Chicken.add_class_trait("hatched_from", Instance(Egg))
