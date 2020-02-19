from traits.api import ListBool, HasTraits


class Test(HasTraits):
    var = ListBool()


obj = Test()
obj.var = []
obj.var = [True]
obj.var = [False]

obj.var = [3 + 5j]  # {ERR}
obj.var = [1, 2, 3]  # {ERR}
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
