#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# wildcard.py --- Example of using a wildcard with a trait
#                 attribute name
from traits.api import Any, HasTraits


class Person(HasTraits):
    temp_ = Any
