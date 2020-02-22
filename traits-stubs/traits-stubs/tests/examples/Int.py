from traits.api import HasTraits, Int


class Test(HasTraits):
    i = Int()


o = Test()
o.i = "5"  # E: assignment
o.i = 5
o.i = 5.5  # E: assignment


class Test2(HasTraits):
    i = Int(default_value="234", something="else")  # E: arg-type


class Test3(HasTraits):
    i = Int(default_value=234)
