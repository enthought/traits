from traits.api import DictStrAny, HasTraits


class Test(HasTraits):
    var = DictStrAny()


obj = Test()
obj.var = {"a": 5, "b": None, "c": ""}
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
