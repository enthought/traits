#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# list_notifier.py -- Example of zero-parameter handlers for an object
#                     containing a list

#--[Imports]-------------------------------------------------------------------
from traits.api import HasTraits, List


#--[Code]----------------------------------------------------------------------
class Employee:
    pass


class Department(HasTraits):
    employees = List(Employee)


#--[Example*]------------------------------------------------------------------
def a_handler():
    print "A handler"


def b_handler():
    print "B handler"


def c_handler():
    print "C handler"

fred = Employee()
mary = Employee()
donna = Employee()

dept = Department(employees=[fred, mary])

# "Old style" name syntax
# a_handler is called only if the list is replaced:
dept.on_trait_change(a_handler, 'employees')
# b_handler is called if the membership of the list changes:
dept.on_trait_change(b_handler, 'employees_items')

# "New style" name syntax
# c_handler is called if 'employees' or its membership change:
dept.on_trait_change(c_handler, '[employees]')

print "Changing list items"
dept.employees[1] = donna     # Calls B and C
print "Replacing list"
dept.employees = [donna]      # Calls A and C
