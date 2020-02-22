from traits.api import Complex, HasTraits


class Test(HasTraits):
    var = Complex()


obj = Test()
obj.var = "5"  # E: assignment
obj.var = 5
obj.var = 5.5
obj.var = 5 + 4j


class Test2(HasTraits):
    var = Complex(default_value="sdf")  # E: arg-type
