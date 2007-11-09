# keywords.py --- Example of trait keywords
from enthought.traits.api import HasTraits, Trait 

class Person(HasTraits): 
    first_name = Trait('', 
                       desc='first or personal name',
                       label='First Name')
    last_name =  Trait('', 
                       desc='last or family name', 
                       label='Last Name')
