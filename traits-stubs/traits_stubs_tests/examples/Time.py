# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import datetime
from traits.api import HasTraits, Time, Int


class TestClass(HasTraits):
    t = Time()
    x = Int()


obj = TestClass()
obj.t = datetime.time()
obj.t = "sometime-string"
obj.t = datetime.datetime()  # E: assignment, call-arg
obj.t = 9  # E: assignment
obj.t = []  # E: assignment
