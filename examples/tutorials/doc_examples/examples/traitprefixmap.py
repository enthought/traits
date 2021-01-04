# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# traitprefixmap.py --- Example of using the TraitPrefixMap handler

# --[Imports]------------------------------------------------------------------
from traits.api import Trait, TraitPrefixMap

# --[Code]---------------------------------------------------------------------
boolean_map = Trait(
    "true", TraitPrefixMap({"true": 1, "yes": 1, "false": 0, "no": 0})
)
