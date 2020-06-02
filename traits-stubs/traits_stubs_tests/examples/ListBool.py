from traits.api import ListBool, HasTraits


class Test(HasTraits):
    var = ListBool()


obj = Test()
obj.var = []
obj.var = [True]
obj.var = [False]

obj.var = [3 + 5j]  # E: list-item
obj.var = [1, 2, 3]  # E: list-item
obj.var = [1.1]  # E: list-item
obj.var = [1.1, 2, 3.3]  # E: list-item
obj.var = ''  # E: assignment
obj.var = "5"  # E: assignment
obj.var = 5  # E: assignment
obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment
obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment
obj.var = [1, 2, "3"]  # E: list-item
obj.var = None  # E: assignment
obj.var = ['1']  # E: list-item
