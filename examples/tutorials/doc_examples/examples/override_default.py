#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# override_default.py -- Example of overriding a default value for
#                        a trait attribute in a subclass

from traits.api import HasTraits, Range, Str


#--[Code]----------------------------------------------------------------------
# Example of overriding a default value for a trait in a subclass:


# Define the base class:
class Employee(HasTraits):

    name = Str
    salary_grade = Range(value=1, low=1, high=10)


# Define a subclass:
class Manager(Employee):

    # Override the default value for the inherited 'salary_grade' trait:
    salary_grade = 5

#--[Example*]------------------------------------------------------------------
# Create an employee and display its initial contents:
joe = Employee(name='Joe')
joe.print_traits()

# Now do the same thing for a manager object:
mike = Manager(name='Mike')
mike.print_traits()
