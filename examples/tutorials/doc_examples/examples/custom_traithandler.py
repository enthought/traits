#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# custom_traithandler.py --- Example of a custom TraitHandler

#--[Imports]-------------------------------------------------------------------
from traits.api import TraitHandler


#--[Code]----------------------------------------------------------------------
class TraitOddInteger(TraitHandler):

    def validate(self, object, name, value):
        if (isinstance(value, int) and
           (value > 0) and ((value % 2) == 1)):
            return value
        self.error(object, name, value)

    def info(self):
        return 'a positive odd integer'
