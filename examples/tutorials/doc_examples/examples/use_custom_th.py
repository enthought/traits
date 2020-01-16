# use_custom_th.py --- Example of using a custom TraitHandler

# --[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Range, Trait
from custom_traithandler import TraitOddInteger


# --[Code]----------------------------------------------------------------------
class AnOddClass(HasTraits):
    oddball = Trait(1, TraitOddInteger())
    very_odd = Trait(-1, TraitOddInteger(), Range(-10, -1))
