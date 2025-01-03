# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, String


class Test(HasTraits):
    var = String()


obj = Test()
obj.var = "5"
obj.var = 5  # E: assignment

obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment

obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment


class Test2(HasTraits):
    var = String(minlen=5, something="else", regex=r"5")


class Test3(HasTraits):
    var = String(minlen="5")  # E: arg-type
