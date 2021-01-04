# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# bad_self_ref.py -- Non-working example with self-referencing class definition

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Instance

# --[Code]---------------------------------------------------------------------
# Shows the incorrect way of defining a self-referencing class.
try:

    class Employee(HasTraits):

        # This won't work.
        # 'Employee' is not defined until the class definition is complete:
        manager = Instance(Employee)


except NameError as excp:
    print(excp)
