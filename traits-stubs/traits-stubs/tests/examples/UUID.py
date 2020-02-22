import uuid
from traits.api import HasTraits, UUID


class Test(HasTraits):
    var = UUID()


obj = Test()
obj.var = uuid.UUID()

obj.var = "someuuid"

obj.var = 5  # E: assignment

obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment

obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment

obj.var = (True,)  # E: assignment
