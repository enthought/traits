from math import pow
from traits.api import HasTraits, Callable


class Test(HasTraits):
    var = Callable()


obj = Test()
obj.var = pow
obj.var = None

obj.var = "someuuid"  # E: assignment

obj.var = 5  # E: assignment

obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment

obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment

obj.var = (True,)  # E: assignment
