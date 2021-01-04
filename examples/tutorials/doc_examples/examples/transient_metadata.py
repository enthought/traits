# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# transient_metadata.py - Example of using 'transient' metadata

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, File, Any


# --[Code]---------------------------------------------------------------------
class DataBase(HasTraits):

    # The name of the data base file:
    file_name = File

    # The open file handle used to access the data base:
    file = Any(transient=True)
