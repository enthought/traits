# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, BaseCInt


class TestClass1(HasTraits):
    i = BaseCInt()


o = TestClass1()
o.i = "5"
o.i = 5
o.i = 5.5


class Test(HasTraits):
    i = BaseCInt(default_value="234")  # E: arg-type


class Test2(HasTraits):
    i = BaseCInt(default_value=234)
