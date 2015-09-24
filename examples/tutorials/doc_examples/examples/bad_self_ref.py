#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# bad_self_ref.py -- Non-working example with self-referencing class definition

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, Instance

#--[Code]----------------------------------------------------------------------
# Shows the incorrect way of defining a self-referencing class.
try:
    class Employee(HasTraits):

        # This won't work.
        # 'Employee' is not defined until the class definition is complete:
        manager = Instance(Employee)
except NameError, excp:
    print excp
