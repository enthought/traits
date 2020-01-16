# temp_wildcard.py --- Example of using a wildcard with a trait
#                 attribute name

# --[Imports]-------------------------------------------------------------------
from traits.api import Any, HasTraits


# --[Code]----------------------------------------------------------------------
class Person(HasTraits):
    temp_ = Any
