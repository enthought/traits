# this.py --- Example of This predefined trait
from enthought.traits.api import HasTraits, This

class Employee(HasTraits):
    manager = This
