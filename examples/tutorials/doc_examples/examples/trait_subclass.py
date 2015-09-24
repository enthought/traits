#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# trait_subclass.py -- Example of subclassing a trait class

from traits.api import BaseInt


#--[Code]----------------------------------------------------------------------
class OddInt(BaseInt):

    # Define the default value
    default_value = 1

    # Describe the trait type
    info_text = 'an odd integer'

    def validate(self, object, name, value):
        value = super(OddInt, self).validate(object, name, value)
        if (value % 2) == 1:
            return value

        self.error(object, name, value)
