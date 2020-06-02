import datetime
from traits.api import HasTraits, Time, Int


class TestClass(HasTraits):
    t = Time()
    x = Int()


obj = TestClass()
obj.t = datetime.time()
obj.t = "sometime-string"
obj.t = datetime.datetime()  # E: assignment, call-arg
obj.t = 9  # E: assignment
obj.t = []  # E: assignment
