# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# trait_subclass.py -- Example of subclassing a trait class

from traits.api import BaseInt


# --[Code]---------------------------------------------------------------------
class OddInt(BaseInt):

    # Define the default value
    default_value = 1

    # Describe the trait type
    info_text = "an odd integer"

    def validate(self, object, name, value):
        value = super().validate(object, name, value)
        if (value % 2) == 1:
            return value

        self.error(object, name, value)
