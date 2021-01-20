# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# instance_trait_defaults.py --- Example of Instance trait default values

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Instance


# --[Code]---------------------------------------------------------------------
class Parent(HasTraits):
    pass


class Child(HasTraits):
    # default value is None
    father = Instance(Parent)
    # default value is still None, but None can not be assigned
    grandfather = Instance(Parent, allow_none=False)
    # default value is Parent()
    mother = Instance(Parent, args=())
