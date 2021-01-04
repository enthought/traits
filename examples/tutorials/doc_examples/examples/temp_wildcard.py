# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# temp_wildcard.py --- Example of using a wildcard with a trait
#                 attribute name

# --[Imports]------------------------------------------------------------------
from traits.api import Any, HasTraits


# --[Code]---------------------------------------------------------------------
class Person(HasTraits):
    temp_ = Any
