from traits.api import HasTraits, Int, List


class Test(HasTraits):
    var = List(Int())


obj = Test()
obj.var = "5"  # {ERR}
obj.var = 5  # {ERR}

obj.var = False  # {ERR}
obj.var = 5.5  # {ERR}

obj.var = 5 + 4j  # {ERR}
obj.var = True  # {ERR}

obj.var = [1, 2, 3]
obj.var = [1, 2, "3"]  # {ERR}
