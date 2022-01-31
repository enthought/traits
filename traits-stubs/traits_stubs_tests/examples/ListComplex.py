# (C) Copyright 2005-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import ListComplex, HasTraits


class Test(HasTraits):
    var = ListComplex()


obj = Test()
obj.var = []
obj.var = [3 + 5j]
obj.var = [1, 2, 3]
obj.var = [1.1]
obj.var = [1.1, 2, 3.3]

obj.var = ''  # E: assignment
obj.var = "5"  # E: assignment
obj.var = 5  # E: assignment
obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment
obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment
obj.var = [1, 2, "3"]  # E: list-item
obj.var = None  # E: assignment
obj.var = ['1']  # E: list-item
