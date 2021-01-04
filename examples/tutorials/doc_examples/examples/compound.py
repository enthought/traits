# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# compound.py -- Example of multiple criteria in a trait definition


# --[Imports]------------------------------------------------------------------
from traits.api import HasTraits, Range, Trait, TraitError


# --[Code]---------------------------------------------------------------------
# Shows the definition of a compound trait.


class Die(HasTraits):

    # Define a compound trait definition:
    value = Trait(1, Range(1, 6), "one", "two", "three", "four", "five", "six")


# --[Example*]-----------------------------------------------------------------
# Create a sample Die:
die = Die()

# Try out some sample valid values:
die.value = 3
die.value = "three"
die.value = 5
die.value = "five"

# Now try out some invalid values:
try:
    die.value = 0
except TraitError as excp:
    print(excp)

try:
    die.value = "zero"
except TraitError as excp:
    print(excp)
