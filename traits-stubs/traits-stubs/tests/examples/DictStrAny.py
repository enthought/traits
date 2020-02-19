from traits.api import ListInt, HasTraits


class Test(HasTraits):
    var = ListInt()


obj = Test()
obj.var = []
obj.var = [1, 2, 3]

obj.var = [1.1]  # {ERR}
obj.var = [1.1, 2, 3.3]  # {ERR}
obj.var = ''  # {ERR}
obj.var = "5"  # {ERR}
obj.var = 5  # {ERR}
obj.var = False  # {ERR}
obj.var = 5.5  # {ERR}
obj.var = 5 + 4j  # {ERR}
obj.var = True  # {ERR}
obj.var = [1, 2, "3"]  # {ERR}
obj.var = None  # {ERR}
obj.var = ['1']  # {ERR}
