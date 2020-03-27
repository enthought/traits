from traits.api import HasTraits, String


class Test(HasTraits):
    var = String()


obj = Test()
obj.var = "5"
obj.var = 5  # E: assignment

obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment

obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment


class Test2(HasTraits):
    var = String(minlen=5, something="else", regex=r"5")


class Test3(HasTraits):
    var = String(minlen="5")  # E: arg-type
