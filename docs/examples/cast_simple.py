# cast_simple.py --- Example of using simple cast types
from enthought.traits.api import HasTraits, CStr, CFloat

class Person(HasTraits):
    name = CStr
    weight = CFloat
