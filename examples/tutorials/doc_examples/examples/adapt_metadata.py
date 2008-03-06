# adapt_metadata.py – Example of using 'adapt' metadata

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import HasTraits, Instance
from interface_definition import IName

#--[Code]-----------------------------------------------------------------------

class Apartment( HasTraits ):
    renter = Instance( IName, adapt='no' )

