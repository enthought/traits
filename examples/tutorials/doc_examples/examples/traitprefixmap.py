#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# traitprefixmap.py --- Example of using the TraitPrefixMap handler

#--[Imports]-------------------------------------------------------------------
from traits.api import Trait, TraitPrefixMap

#--[Code]----------------------------------------------------------------------
boolean_map = Trait('true',
                    TraitPrefixMap({
                        'true': 1,
                        'yes': 1,
                        'false': 0,
                        'no': 0})
                    )
