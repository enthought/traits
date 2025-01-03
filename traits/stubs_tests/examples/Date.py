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
from traits.api import HasTraits, Date, Int


class TestClass(HasTraits):
    t = Date()
    x = Int()


obj = TestClass()
obj.t = datetime.datetime.now().date()
obj.t = datetime.datetime.now()
obj.t = None

obj.t = datetime.datetime.now().time()  # E: assignment
obj.t = "sometime-string"  # E: assignment
obj.t = 9  # E: assignment
obj.t = []  # E: assignment
