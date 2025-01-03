# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, Str


class Test(HasTraits):
    i = Str()


o = Test()
o.i = "5"
o.i = 5  # E: assignment
o.i = 5.5  # E: assignment


class Test2(HasTraits):
    var = Str(default_value=None)  # E: arg-type
