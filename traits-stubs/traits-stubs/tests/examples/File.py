from pathlib import Path, PosixPath
from traits.api import HasTraits, BaseFile, File


class Test(HasTraits):
    var = BaseFile()
    var2 = File()


obj = Test()
obj.var = Path('/tmp')
obj.var = PosixPath('/tmp')
obj.var = "someuuid"

obj.var2 = Path('/tmp')
obj.var2 = PosixPath('/tmp')
obj.var2 = "someuuid"

obj.var = 5  # {ERR}

obj.var = False  # {ERR}
obj.var = 5.5  # {ERR}

obj.var = 5 + 4j  # {ERR}
obj.var = True  # {ERR}

obj.var = (True,)  # {ERR}
