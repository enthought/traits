from traits.api import HasTraits, String


class Test(HasTraits):
    var = String()


obj = Test()
obj.var = "5"
obj.var = 5  # {ERR}

obj.var = False  # {ERR}
obj.var = 5.5  # {ERR}

obj.var = 5 + 4j  # {ERR}
obj.var = True  # {ERR}


class Test2(HasTraits):
    var = String(minlen=5, something="else", regex=r"5")


class Test3(HasTraits):
    var = String(minlen="5")  # {ERR}
