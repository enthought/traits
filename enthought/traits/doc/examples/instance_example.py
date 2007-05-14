# instance_example.py --- Example of Instance() trait factory
from enthought.traits.api import HasTraits, Instance, Int, Str, Trait

class Person(HasTraits):
    name = Trait('')
    age = Trait(0)

bill = Person()
bill.name = 'William'

class EmployeeInfo(HasTraits):
    worker = Instance(Person)
    manager = Instance(bill)

