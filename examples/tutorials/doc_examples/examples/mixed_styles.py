#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# mixed_styles.py -- Example of using editor styles at various levels

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasTraits, Str, Enum
from enthought.traits.ui.api import View, Group, Item

#--[Code]-----------------------------------------------------------------------

class MixedStyles(HasTraits):
   first_name = Str
   last_name = Str

   department = Enum("Business", "Research", "Admin")
   position_type = Enum("Full-Time", 
                        "Part-Time", 
                        "Contract")

   traits_view = View(Group(Item(name='first_name'),
                            Item(name='last_name'),
                            Group(Item(name='department'),
                                  Item(name= 
                                          'position_type',
                                       style='custom'),
                                  style='simple')),
                      title='Mixed Styles',
                      style='readonly')

ms = MixedStyles(first_name='Sam', last_name='Smith')
ms.configure_traits()

