from traits.api import Float, HasTraits


class Test(HasTraits):
    i = Float()


o = Test()
o.i = "5"  # {ERR}
o.i = 5
o.i = 5.5
