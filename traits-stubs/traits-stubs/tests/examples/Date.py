import datetime
from traits.api import HasTraits, Date, Int


class TestClass(HasTraits):
    t = Date()
    x = Int()


obj = TestClass()
obj.t = datetime.datetime.now()
obj.t = datetime.datetime.now().date()
obj.t = "sometime-string"

obj.t = datetime.datetime.now().time()  # E: assignment
obj.t = 9  # E: assignment
obj.t = []  # E: assignment
