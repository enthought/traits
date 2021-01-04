# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# prototype_prefix.py --- Examples of PrototypedFrom() prefix parameter

# --[Imports]------------------------------------------------------------------
from traits.api import PrototypedFrom, Float, HasTraits, Instance, Str


# --[Code]---------------------------------------------------------------------
class Parent(HasTraits):
    first_name = Str
    family_name = ""
    favorite_first_name = Str
    child_allowance = Float(1.00)


class Child(HasTraits):
    __prefix__ = "child_"
    first_name = PrototypedFrom("mother", "favorite_*")
    last_name = PrototypedFrom("father", "family_name")
    allowance = PrototypedFrom("father", "*")
    father = Instance(Parent)
    mother = Instance(Parent)


# --[Example*]-----------------------------------------------------------------
fred = Parent(
    first_name="Fred",
    family_name="Lopez",
    favorite_first_name="Diego",
    child_allowance=5.0,
)

maria = Parent(
    first_name="Maria",
    family_name="Gonzalez",
    favorite_first_name="Tomas",
    child_allowance=10.0,
)

nino = Child(father=fred, mother=maria)

print(
    "%s %s gets $%.2f for allowance"
    % (nino.first_name, nino.last_name, nino.allowance)
)
