from traits.api import HasTraits, Set, Int


class Test(HasTraits):
    var = Set(trait=Int())


obj = Test()
obj.var = "5"  # E: assignment
obj.var = 5  # E: assignment

obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment

obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment

obj.var = [1, 2, 3]  # E: assignment
obj.var = [1, 2, "3"]  # E: assignment

obj.var = {1, 2, 3}
