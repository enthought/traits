import uuid
from traits.api import HasTraits, UUID


class Test(HasTraits):
    var = UUID()


obj = Test()
obj.var = uuid.UUID()

obj.var = "someuuid"

obj.var = 5  # {ERR}

obj.var = False  # {ERR}
obj.var = 5.5  # {ERR}

obj.var = 5 + 4j  # {ERR}
obj.var = True  # {ERR}

obj.var = (True,)  # {ERR}
