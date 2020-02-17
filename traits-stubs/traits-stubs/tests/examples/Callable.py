from math import pow
from traits.api import HasTraits, Callable


class Test(HasTraits):
    var = Callable()


obj = Test()
obj.var = pow
obj.var = None

obj.var = "someuuid"  # {ERR}

obj.var = 5  # {ERR}

obj.var = False  # {ERR}
obj.var = 5.5  # {ERR}

obj.var = 5 + 4j  # {ERR}
obj.var = True  # {ERR}

obj.var = (True,)  # {ERR}
