# default_trait_ui.py --- Example of the default 
#                         attribute-editing window 
#                         provided by Traits
from enthought.traits.api import HasTraits, Int, Str, Trait
import enthought.traits.ui

class Person(HasTraits):
    first_name = Str
    last_name = Str
    age = Int
    gender = Trait(None, 'M', 'F')

bill = Person()
bill.configure_traits(kind='modal')
