#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# interface_definition.py - Example of defining an interface

#--[Imports]-------------------------------------------------------------------
from traits.api import Interface


#--[Code]----------------------------------------------------------------------
class IName(Interface):

    def get_name(self):
        """ Returns a string which is the name of an object. """
