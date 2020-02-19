from traits.api import ListComplex, HasTraits


class Test(HasTraits):
    var = ListComplex()


obj = Test()
obj.var = []
obj.var = [3 + 5j]
obj.var = [1, 2, 3]
obj.var = [1.1]
obj.var = [1.1, 2, 3.3]

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
