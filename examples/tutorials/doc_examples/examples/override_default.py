# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# override_default.py -- Example of overriding a default value for
#                        a trait attribute in a subclass

from traits.api import HasTraits, Range, Str


# --[Code]---------------------------------------------------------------------
# Example of overriding a default value for a trait in a subclass:


# Define the base class:
class Employee(HasTraits):

    name = Str
    salary_grade = Range(value=1, low=1, high=10)


# Define a subclass:
class Manager(Employee):

    # Override the default value for the inherited 'salary_grade' trait:
    salary_grade = 5


# --[Example*]-----------------------------------------------------------------
# Create an employee and display its initial contents:
joe = Employee(name="Joe")
joe.print_traits()

# Now do the same thing for a manager object:
mike = Manager(name="Mike")
mike.print_traits()
