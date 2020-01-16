# this.py --- Example of This predefined trait

# --[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, This


# --[Code]----------------------------------------------------------------------
class Employee(HasTraits):
    manager = This
