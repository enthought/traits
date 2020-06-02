from traits.api import Bool, HasTraits


class Test(HasTraits):
    var = Bool()


obj = Test()
obj.var = "5"  # E: assignment
obj.var = 5  # E: assignment

obj.var = False
obj.var = 5.5  # E: assignment

obj.var = 5 + 4j  # E: assignment
obj.var = True
