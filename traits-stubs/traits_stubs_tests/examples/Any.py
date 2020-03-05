from traits.api import HasTraits, Any, Instance, Int
from typing import Any as _Any


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
    # y = Any()


class Subclass(Superclass):
    x = Instance(Foo)
    y = Int()
