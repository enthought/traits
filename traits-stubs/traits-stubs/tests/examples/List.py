from traits.api import HasTraits, Int, List, Any


class Test(HasTraits):
    var = List(Int())


obj = Test()
obj.var = "5"  # {ERR}
obj.var = 5  # {ERR}
obj.var = False  # {ERR}
obj.var = 5.5  # {ERR}
obj.var = 5 + 4j  # {ERR}
obj.var = True  # {ERR}
obj.var = [1.1, 2, 3.3]  # {ERR}
obj.var = [1, 2, "3"]  # {ERR}
obj.var = None  # {ERR}

obj.var = [1, 2, 3]


class TestAnyList(HasTraits):
    var = List(Any())


obj = TestAnyList()
obj.var = "5"
obj.var = 5  # {ERR}
obj.var = False  # {ERR}
obj.var = 5.5  # {ERR}
obj.var = 5 + 4j  # {ERR}
obj.var = True  # {ERR}
obj.var = [1.1, 2, 3.3]
obj.var = [1, 2, "3"]
obj.var = None  # {ERR}

obj.var = [1, 2, 3]


class TestPlainList(HasTraits):
    var = List()  # {ERR}
