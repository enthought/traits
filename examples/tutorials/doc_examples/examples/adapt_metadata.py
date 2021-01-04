# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# adapt_metadata.py - Example of using 'adapt' metadata

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Instance
from interface_definition import IName


# --[Code]---------------------------------------------------------------------
class Apartment(HasTraits):
    renter = Instance(IName, adapt="no")
