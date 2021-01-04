# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# wildcard_rules.py --- Example of trait attribute wildcard rules

# --[Imports]------------------------------------------------------------------
from traits.api import Any, HasTraits, Int, Python


# --[Code]---------------------------------------------------------------------
class Person(HasTraits):
    temp_count = Int(-1)
    temp_ = Any
    _ = Python
