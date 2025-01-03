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

from traits.api import HasTraits, Time


class TestClass(HasTraits):
    t = Time()


obj = TestClass()
obj.t = datetime.time(11, 12, 13)
obj.t = "sometime-string"  # E: assignment
obj.t = datetime.datetime(2020, 1, 1)  # E: assignment
obj.t = 9  # E: assignment
obj.t = []  # E: assignment
