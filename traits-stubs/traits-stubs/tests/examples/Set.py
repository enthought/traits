from traits.api import HasTraits, Set, Int


class Test(HasTraits):
    var = Set(trait=Int())


obj = Test()
obj.var = "5"  # {ERR}
obj.var = 5  # {ERR}

obj.var = False  # {ERR}
obj.var = 5.5  # {ERR}

obj.var = 5 + 4j  # {ERR}
obj.var = True  # {ERR}

obj.var = [1, 2, 3]  # {ERR}
obj.var = [1, 2, "3"]  # {ERR}

obj.var = {1, 2, 3}
