from traits.api import Dict, HasTraits, Str, Any


class Test(HasTraits):
    var = Dict(Str(), Any())


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
