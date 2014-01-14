#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.


# adapt_metadata.py - Example of using 'adapt' metadata

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Instance
from interface_definition import IName


#--[Code]----------------------------------------------------------------------
class Apartment(HasTraits):
    renter = Instance(IName, adapt='no')
