# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# custom_traithandler.py --- Example of a custom TraitHandler

# --[Imports]------------------------------------------------------------------
from traits.api import TraitHandler


# --[Code]---------------------------------------------------------------------
class TraitOddInteger(TraitHandler):
    def validate(self, object, name, value):
        if isinstance(value, int) and (value > 0) and ((value % 2) == 1):
            return value
        self.error(object, name, value)

    def info(self):
        return "a positive odd integer"
