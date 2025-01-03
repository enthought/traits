# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import Dict, HasTraits, Str, Any


class Test(HasTraits):
    var = Dict(Str(), Any())


obj = Test()
obj.var = {"a": 5, "b": None, "c": ""}
obj.var = []  # E: assignment
obj.var = [1, 2, 3]  # E: assignment
obj.var = [1.1]  # E: assignment
obj.var = [1.1, 2, 3.3]  # E: assignment
obj.var = ''  # E: assignment
obj.var = "5"  # E: assignment
obj.var = 5  # E: assignment
obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment
obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment
obj.var = [1, 2, "3"]  # E: assignment
obj.var = None  # E: assignment
obj.var = ['1']  # E: assignment
