# bad_self_ref.py --- Non-working example with self-
#                     referencing class definition
from enthought.traits.api import HasTraits, Trait

class Employee(HasTraits):
    manager = Trait(Employee)
