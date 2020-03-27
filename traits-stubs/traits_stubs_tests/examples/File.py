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

obj.var = 5  # E: assignment

obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment

obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment

obj.var = (True,)  # E: assignment
