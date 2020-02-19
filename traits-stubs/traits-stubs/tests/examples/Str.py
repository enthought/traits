from traits.api import HasTraits, Str


class Test(HasTraits):
    i = Str()


o = Test()
o.i = "5"
o.i = 5  # {ERR}
o.i = 5.5  # {ERR}


class Test2(HasTraits):
    var = Str(default_value=None)  # {ERR}
