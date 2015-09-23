#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

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
bill.configure_traits(kind='modal')
