from traits.api import Event, HasStrictTraits, observe


class Person(HasStrictTraits):
    conductor = Event()

    @observe("conductor")
    def talk(self, event):
        pass


def sing(event):
    pass


person = Person()
person.observe(sing, "conductor")
