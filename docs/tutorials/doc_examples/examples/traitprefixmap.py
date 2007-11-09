# traitprefixmap.py --- Example of TraitPrefixMap 
#                       handler
from enthought.traits.api import Trait, TraitPrefixMap

boolean_map = Trait('true', TraitPrefixMap( {
                              'true': 1,
                              'yes':  1,
                              'false': 0,
                              'no':   0 } ) )
