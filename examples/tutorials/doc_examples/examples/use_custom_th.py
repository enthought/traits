# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# use_custom_th.py --- Example of using a custom TraitHandler

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Range, Trait
from custom_traithandler import TraitOddInteger


# --[Code]---------------------------------------------------------------------
class AnOddClass(HasTraits):
    oddball = Trait(1, TraitOddInteger())
    very_odd = Trait(-1, TraitOddInteger(), Range(-10, -1))
