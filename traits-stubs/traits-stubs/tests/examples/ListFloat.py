from traits.api import ListInt, HasTraits


class Test(HasTraits):
    var = ListInt()


obj = Test()
obj.var = ['1']  # {ERR}
obj.var = [1]  # {ERR}
obj.var = ''  # {ERR}
