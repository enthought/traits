# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, Any, Instance, Int


class Test(HasTraits):
    i = Any()


obj = Test()
obj.i = "5"
obj.i = 5
obj.i = 5.5
obj.i = {"a": 5, "b": 6}
obj.i = {"a": 5.5, "b": 6}
obj.i = {"a": 5, "b": None, "c": ""}
obj.i = []
obj.i = [1, 2, 3]
obj.i = [1.1]
obj.i = [1.1, 2, 3.3]
obj.i = ''
obj.i = "5"
obj.i = 5
obj.i = False
obj.i = 5.5
obj.i = 5 + 4j
obj.i = True
obj.i = [1, 2, "3"]
obj.i = None
obj.i = ['1']


class Test2(HasTraits):
    i = Any(default_value="234")


class Test3(HasTraits):
    i = Any(default_value=234)


class Foo:
    pass


class Superclass(HasTraits):
    x = Any()


class Subclass(Superclass):
    x = Instance(Foo)  # E: assignment
    y = Int()
