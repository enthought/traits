# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# keywords.py --- Example of trait keywords

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Str


# --[Code]---------------------------------------------------------------------
class Person(HasTraits):
    # 'label' is used for Traits UI field labels;
    # 'desc' can be used for tooltips.
    first_name = Str("", desc="first or personal name", label="First Name")
    last_name = Str("", desc="last or family name", label="Last Name")
