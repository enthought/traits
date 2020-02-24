from traits.api import HasTraits, Int


class Test(HasTraits):
    i = Int()
    j = Int(default_value="234")  # E: arg-type
    k = Int(default_value=234, something="else")


o = Test()
o.i = 5

o.i = "5"  # E: assignment
o.i = 5.5  # E: assignment
o.i = 5.5 + 5  # E: assignment
o.i = str(5)  # E: assignment
o.i = None  # E: assignment


# Test subclassing Int
class Digit(Int):
    def validate(self, object, name, value):
        if isinstance(value, int) and 0 <= value <= 9:
            return value

        self.error(object, name, value)


class TestClass2(HasTraits):
    i = Digit()


obj = TestClass2()
obj.i = 5
obj.i = "5"  # E: assignment
