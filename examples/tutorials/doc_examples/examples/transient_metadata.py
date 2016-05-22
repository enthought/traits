#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# transient_metadata.py - Example of using 'transient' metadata

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, File, Any


#--[Code]----------------------------------------------------------------------
class DataBase(HasTraits):

    # The name of the data base file:
    file_name = File

    # The open file handle used to access the data base:
    file = Any(transient=True)
