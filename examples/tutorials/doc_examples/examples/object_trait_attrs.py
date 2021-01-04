# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# object_trait_attrs.py --- Example of per-object trait attributes

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Range


# --[Code]---------------------------------------------------------------------
class GUISlider(HasTraits):
    def __init__(
        self,
        eval=None,
        label="Value",
        trait=None,
        min=0.0,
        max=1.0,
        initial=None,
        **traits
    ):
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
