# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import datetime

from traits.api import Datetime, HasTraits


class TestClass(HasTraits):
    t = Datetime()


obj = TestClass()
obj.t = "sometime-string"  # E: assignment
obj.t = datetime.datetime.now()

obj.t = 9  # E: assignment
obj.t = []  # E: assignment
obj.t = datetime.datetime.now().date()  # E: assignment
