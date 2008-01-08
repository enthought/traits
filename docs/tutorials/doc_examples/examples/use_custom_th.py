# use_custom_th.py --- Example of using a custom TraitHandler

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasTraits, Trait, TraitRange
from custom_traithandler import TraitOddInteger

#--[Code]-----------------------------------------------------------------------
class AnOddClass(HasTraits):
    oddball = Trait(1, TraitOddInteger())
    very_odd = Trait(-1, TraitOddInteger(), 
                         TraitRange(-10, -1))
