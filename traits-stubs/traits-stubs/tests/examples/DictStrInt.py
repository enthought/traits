from traits.api import DictStrInt, HasTraits


class Test(HasTraits):
    var = DictStrInt()


obj = Test()
obj.var = {"a": 5, "b": 6}

obj.var = {"a": 5, "b": 6.6}  # {ERR}
obj.var = {"a": 5, "b": None, "c": ""}  # {ERR}
obj.var = []  # {ERR}
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
