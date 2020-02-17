from traits.api import HasTraits, Range


class Test(HasTraits):
    var = Range(low=[])  # {ERR}
    var2 = Range(low="3")
    var3 = Range(low=3)


obj = Test()
