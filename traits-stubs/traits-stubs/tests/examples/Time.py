import datetime
from traits.api import HasTraits, Time, Int


class TestClass(HasTraits):
    t = Time()
    x = Int()


obj = TestClass()
obj.t = datetime.time()
obj.t = "sometime-string"
obj.t = datetime.datetime()  # {ERR}
obj.t = 9  # {ERR}
obj.t = []  # {ERR}
