# override_default.py -- Example of overriding a default value 
#                        for a trait attribute in a subclass
from enthought.traits.api import HasTraits, Range

class Employee(HasTraits):
    name = Str
    salary_grade = Range(value=1, low=1, high=10)
    
class Manager(Employee):
    salary_grade = 5
