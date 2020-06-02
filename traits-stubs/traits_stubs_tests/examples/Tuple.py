from traits.api import HasTraits, Tuple


class Test(HasTraits):
    var = Tuple(1, 2, 3)


obj = Test()
obj.var = "5"  # E: assignment
obj.var = 5  # E: assignment

obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment

obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment

obj.var = (True,)
