#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.


# all_wildcard.py --- Example of trait attribute wildcard rules

# --[Imports]-------------------------------------------------------------------
from traits.api import Any, Str, Int, HasTraits, TraitError


# --[Code]----------------------------------------------------------------------
class Person(HasTraits):

    # Normal, explicitly defined trait:
    name = Str

    # By default, let all traits have any value:
    _ = Any

    # Except for this one, which must be an Int:
    age = Int


# --[Example*]------------------------------------------------------------------
# Create a sample Person:
bill = Person()

# These assignments should all work:
bill.name = "William"
bill.address = "121 Drury Lane"
bill.zip_code = 55212
bill.age = 49

# This should generate an error (must be an Int):
print("Attempting to assign a string to an Int trait object...\n")
try:
    bill.age = "middle age"
except TraitError as c:
    print("TraitError: ", c, "\n")

# Display the final results:
bill.print_traits()
