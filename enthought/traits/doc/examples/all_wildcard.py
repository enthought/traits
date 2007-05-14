# all_wildcard.py --- Example of trait attribute wildcard rules
from enthought.traits.api import Any, HasTraits

class Person(HasTraits):
    _ = Any 
    
