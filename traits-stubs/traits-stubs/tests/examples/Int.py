from traits.api import HasTraits, Int


class Test(HasTraits):
    i = Int()


o = Test()
o.i = "5"  # {ERR}
o.i = 5
o.i = 5.5  # {ERR}


class Test2(HasTraits):
    i = Int(default_value="234", something="else")  # {ERR}


class Test3(HasTraits):
    i = Int(default_value=234)
