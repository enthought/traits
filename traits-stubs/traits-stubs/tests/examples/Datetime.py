import datetime
from traits.api import HasTraits, Datetime, Int


class TestClass(HasTraits):
    t = Datetime()
    x = Int()


obj = TestClass()
obj.t = "sometime-string"
obj.t = datetime.datetime.now()

obj.t = 9  # {ERR}
obj.t = []  # {ERR}
obj.t = datetime.datetime.now.date()  # {ERR}
