from traits.api import ListComplex, HasTraits


class Test(HasTraits):
    var = ListComplex()


obj = Test()
obj.var = []
obj.var = [3 + 5j]
obj.var = [1, 2, 3]
obj.var = [1.1]
obj.var = [1.1, 2, 3.3]

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
