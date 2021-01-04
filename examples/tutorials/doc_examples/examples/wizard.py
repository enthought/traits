# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# wizard.py ---Example of a traits-based wizard UI
from traits.api import HasTraits, Int, Str


class Person(HasTraits):
    name = Str
    age = Int
    street = Str
    city = Str
    state = Str
    pcode = Str


bill = Person()
bill.configure_traits(kind="modal")
