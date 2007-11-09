# traitstring.py --- Example of TraitString trait 
#                    handler class
from enthought.traits.api import HasTraits, Trait, TraitString

class Person(HasTraits):
    name=Trait('', TraitString(maxlen=50, regex=r'^[A-Za-z]*$'))
