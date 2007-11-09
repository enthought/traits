# traitprefixlist.py --- Example of using the TraitPrefixList
#                        class
from enthought.traits.api import HasTraits, Trait, TraitPrefixList

class Person(HasTraits):
    married = Trait('no', TraitPrefixList('yes', 'no'))
