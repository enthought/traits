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
