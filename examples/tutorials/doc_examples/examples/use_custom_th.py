#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# use_custom_th.py --- Example of using a custom TraitHandler

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Trait, TraitRange
from custom_traithandler import TraitOddInteger


#--[Code]----------------------------------------------------------------------
class AnOddClass(HasTraits):
    oddball = Trait(1, TraitOddInteger())
    very_odd = Trait(-1, TraitOddInteger(),
                     TraitRange(-10, -1))
