# all_traits_features.py --- Shows primary features of the Traits 
#                            package
from enthought.traits.api import Delegate, HasTraits, Int, Trait
import enthought.traits.ui

class Parent(HasTraits):
    last_name = Trait('') # INITIALIZATION: 
                          #'last_name' is 
                          # initialized to ''
    
class Child(HasTraits):
    age = Int
    father = Trait(Parent) # VALIDATION: 'father' must 
                           # be a Parent instance
    last_name = Delegate('father') # DELEGATION: 
                                   # 'last_name' is 
                                   # delegated to 
                                   # father's 'last_name'
    
    def _age_changed(self, old, new): # NOTIFICATION: 
                                      # This method is 
                                      # called when 'age' 
                                      # changes
        print 'Age changed from %s to %s ' % (old, new)

"""
>>> joe = Parent()
>>> joe.last_name = 'Johnson'
>>> moe = Child()
>>> moe.father = joe
>>> # DELEGATION in action
>>> print "Moe's last name is %s " % (moe.last_name) 
Moe's last name is Johnson
>>> # NOTIFICATION in action
>>> moe.age = 10
Age changed from 0 to 10
>>> # VISUALIZATION: Displays a UI for editing moe's 
>>> # attributes (if a supported GUI toolkit is installed)
>>> moe.configure_traits()
"""
