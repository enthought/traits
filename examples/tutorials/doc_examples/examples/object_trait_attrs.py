#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# object_trait_attrs.py --- Example of per-object trait attributes

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Range


#--[Code]----------------------------------------------------------------------
class GUISlider(HasTraits):

    def __init__(self, eval=None, label='Value',
                 trait=None, min=0.0, max=1.0,
                 initial=None, **traits):
        HasTraits.__init__(self, **traits)
        if trait is None:
            if min > max:
                min, max = max, min
            if initial is None:
                initial = min
            elif not (min <= initial <= max):
                initial = [min, max][abs(initial - min) > abs(initial - max)]
            trait = Range(min, max, value=initial)
        self.add_trait(label, trait)
