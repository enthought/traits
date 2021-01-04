# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# list_notifier.py -- Example of zero-parameter handlers for an object
#                     containing a list

# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, List


# --[Code]---------------------------------------------------------------------
class Employee:
    pass


class Department(HasTraits):
    employees = List(Employee)


# --[Example*]-----------------------------------------------------------------
def a_handler():
    print("A handler")


def b_handler():
    print("B handler")


def c_handler():
    print("C handler")


fred = Employee()
mary = Employee()
donna = Employee()

dept = Department(employees=[fred, mary])

# "Old style" name syntax
# a_handler is called only if the list is replaced:
dept.on_trait_change(a_handler, "employees")
# b_handler is called if the membership of the list changes:
dept.on_trait_change(b_handler, "employees_items")

# "New style" name syntax
# c_handler is called if 'employees' or its membership change:
dept.on_trait_change(c_handler, "[employees]")

print("Changing list items")
dept.employees[1] = donna  # Calls B and C
print("Replacing list")
dept.employees = [donna]  # Calls A and C
