#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# disallow.py --- Example of using Disallow with wildcards

#--[Imports]-------------------------------------------------------------------
from traits.api import Disallow, Float, HasTraits, Int, Str


#--[Code]----------------------------------------------------------------------
class Person(HasTraits):
    name = Str
    age = Int
    weight = Float
    _ = Disallow
