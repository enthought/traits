# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, BaseInstance


class Animal:
    pass


class Goldfish(Animal):
    pass


class Leprechaun:
    pass


class Test(HasTraits):
    animal = BaseInstance("Animal")
    animal2 = BaseInstance(Animal)


t = Test()
t.animal = Goldfish()
t.animal = Leprechaun()
t.animal = None
t.animal = Goldfish
t.animal = "sdf"
