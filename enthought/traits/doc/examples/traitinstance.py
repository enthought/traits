# traitinstance.py --- Example of using the TraitInstance class
from enthought.traits.api import HasTraits, Trait, TraitInstance

class Person:
    pass

class Employee(HasTraits):
    manager = Trait(None, TraitInstance(Person, True))
    
