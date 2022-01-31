# (C) Copyright 2005-2022 Enthought, Inc., Austin, TX
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
obj.var = {"a": 5, "b": 6}
obj.var = {"a": 5.5, "b": 6}
obj.var = {"a": 5, "b": None, "c": ""}
obj.var = []
obj.var = [1, 2, 3]
obj.var = [1.1]
obj.var = [1.1, 2, 3.3]
obj.var = ''
obj.var = "5"
obj.var = 5
obj.var = False
obj.var = 5.5
obj.var = 5 + 4j
obj.var = True
obj.var = [1, 2, "3"]
obj.var = None
obj.var = ['1']


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
