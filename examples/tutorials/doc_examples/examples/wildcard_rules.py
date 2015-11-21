#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# wildcard_rules.py --- Example of trait attribute wildcard rules

#--[Imports]-------------------------------------------------------------------
from traits.api import Any, HasTraits, Int, Python


#--[Code]----------------------------------------------------------------------
class Person(HasTraits):
    temp_count = Int(-1)
    temp_ = Any
    _ = Python
