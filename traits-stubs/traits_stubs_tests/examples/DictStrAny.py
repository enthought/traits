from traits.api import DictStrAny, HasTraits


class Test(HasTraits):
    var = DictStrAny()


obj = Test()
obj.var = {"a": 5, "b": None, "c": ""}
obj.var = []  # E: assignment
obj.var = [1, 2, 3]  # E: assignment
obj.var = [1.1]  # E: assignment
obj.var = [1.1, 2, 3.3]  # E: assignment
obj.var = ''  # E: assignment
obj.var = "5"  # E: assignment
obj.var = 5  # E: assignment
obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment
obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment
obj.var = [1, 2, "3"]  # E: assignment
obj.var = None  # E: assignment
obj.var = ['1']  # E: assignment
