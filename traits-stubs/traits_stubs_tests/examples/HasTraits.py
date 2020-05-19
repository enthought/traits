from traits.api import Event, HasTraits, observe


class Person(HasTraits):
    conductor = Event()

    @observe("conductor")
    def talk(self, event):
        pass


def sing(event):
    pass


person = Person()
person.observe(sing, "conductor")
