#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# default_trait_editors.py -- Example of using default trait editors

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasTraits, Str, Range, Bool
from enthought.traits.ui.api import View, Item

#--[Code]-----------------------------------------------------------------------

class Adult(HasTraits):
    first_name = Str
    last_name = Str
    age = Range(21,99)
    registered_voter = Bool

    traits_view = View(Item(name='first_name'),
                       Item(name='last_name'),
                       Item(name='age'),
                       Item(name='registered_voter'))

alice = Adult(first_name='Alice', 
              last_name='Smith',
              age=42, 
              registered_voter=True)

alice.configure_traits()

