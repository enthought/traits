# interface_definition.py –- Example of defining an interface

#--[Imports]--------------------------------------------------------------------
from enthought.traits.api import Interface

#--[Code]-----------------------------------------------------------------------

class IName(Interface):

    def get_name(self):
        """ Returns a string which is the name of an object. """

