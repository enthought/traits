from traits.api import HasTraits, Int, List, Any


class Test(HasTraits):
    var = List(Int())


obj = Test()
obj.var = "5"  # E: assignment
obj.var = 5  # E: assignment
obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment
obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment
obj.var = [1.1, 2, 3.3]  # E: list-item
obj.var = [1, 2, "3"]  # E: list-item
obj.var = None  # E: assignment

obj.var = [1, 2, 3]


class TestAnyList(HasTraits):
    var = List(Any())


obj = TestAnyList()
obj.var = "5"
obj.var = 5  # E: assignment
obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment
obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment
obj.var = [1.1, 2, 3.3]
obj.var = [1, 2, "3"]
obj.var = None  # E: assignment

obj.var = [1, 2, 3]


class TestPlainList(HasTraits):
    var = List()  # E: var-annotated
