# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Perform timing tests to compare the performance of on_trait_change and observe.

For details on motivation and the varying "scenarios" see the related issue:
enthought/traits#1325
"""

import timeit


# Number of iterations to perform:
N = 10000

# Code template strings to be timed for scenario 1

base_setup = """
from traits.api import (
    HasTraits, Instance, observe, on_trait_change, Property, Str
)
from traits.observation.api import trait
"""

person_construction_template = """
class Person(HasTraits):
    name = Str()
    {decorator}
    def some_method(self):
        pass
"""

person_instantiation_setup_template = base_setup + person_construction_template
instantiate_person = """
Person()
"""

person_name_reassignment_setup_template = person_instantiation_setup_template \
    + "a_person = Person()"
reassign_name = """
a_person.name = ''
"""


def scenario1(decorator):
    """ Time the cases described by scenario 1 using the given method decorator.

    Parameters
    ----------
    decorator - Str
        The string defining the decorator to be used on the method of the
        HasTraits subclass.  e.g. "@observe('name')"

    Returns
    -------
    tuple
        A 3-tuple containing the time to construct the HasTraits subclass, the
        time to instantiate it, and the time to reassign the trait
    """
    construct_person = person_construction_template.format(decorator=decorator)
    construction_time = timeit.timeit(
        construct_person, base_setup, number=N
    )

    instantiate_setup = person_instantiation_setup_template.format(
        decorator=decorator
    )
    instantiation_time = timeit.timeit(
        instantiate_person, instantiate_setup, number=N
    )

    reassign_setup = person_name_reassignment_setup_template.format(
        decorator=decorator
    )
    reassign_person_name_time = timeit.timeit(
        reassign_name, reassign_setup, number=N
    )

    return (construction_time, instantiation_time, reassign_person_name_time)


# Code template strings to be timed for scenario 2

construct_parent_setup = base_setup + """
class Person(HasTraits):
    name = Str()
"""
parent_construction_template = """
class Parent(HasTraits):
    child = Instance(Person)
    {decorator}
    def some_method(self, event):
        pass
"""

parent_instantiation_setup_template = construct_parent_setup \
    + parent_construction_template
instantiate_parent = """
Parent()
"""

child_reassignment_setup_template = parent_instantiation_setup_template \
    + "a_parent = Parent(child=Person())"
reassign_child = """
a_parent.child = Person()
"""

reassign_child_name = """
a_parent.child.name = ''
"""


def scenario2(decorator):
    """ Time the cases described by scenario 2 using the given method decorator.

    Parameters
    ----------
    decorator - Str
        The string defining the decorator to be used on the method of the
        HasTraits subclass.  e.g. "@observe('child.name')"

    Returns
    -------
    tuple
        A 4-tuple containing the time to construct the HasTraits subclass, the
        time to instantiate it, the time to reassign child, and the
        time to reassign child.name
    """
    construct_parent = parent_construction_template.format(
        decorator=decorator
    )
    construction_time = timeit.timeit(
        construct_parent, construct_parent_setup, number=N
    )

    instantiate_parent_setup = parent_instantiation_setup_template.format(
        decorator=decorator
    )
    instantiation_time = timeit.timeit(
        instantiate_parent, instantiate_parent_setup, number=N
    )

    reassign_child_setup = child_reassignment_setup_template.format(
        decorator=decorator
    )
    reassign_child_time = timeit.timeit(
        reassign_child, reassign_child_setup, number=N
    )

    reassign_child_name_time = timeit.timeit(
        reassign_child_name, reassign_child_setup, number=N
    )

    return (
        construction_time,
        instantiation_time,
        reassign_child_time,
        reassign_child_name_time
    )


# Code template strings to be timed for scenario 3

person_with_property_construction_template = """
class Person(HasTraits):
    name=Str()
    a_property = Property({})
"""

person_with_property_instantiation_setup_template = base_setup \
    + person_with_property_construction_template

dependee_name_reassignment_setup_template = \
    person_with_property_instantiation_setup_template + "a_person = Person()"


def scenario3(property_args):
    """ Time the cases described by scenario 3 using the given argument to the
    Property trait defintion.

    Parameters
    ----------
    property_args - Str
        The string defining the argument to be passed in the definition of the
        Property trait.  e.g. "depends_on='name'"

    Returns
    -------
    tuple
        A 3-tuple containing the time to construct the HasTraits subclass, the
        time to instantiate it, and the time to reassign the trait being
        depended-on / observed.
    """
    construct_person_with_property = \
        person_with_property_construction_template.format(property_args)
    construction_time = timeit.timeit(
        construct_person_with_property, base_setup, number=N
    )

    instantiate_person_with_property_setup = \
        person_with_property_instantiation_setup_template.format(property_args)
    instantiation_time = timeit.timeit(
        instantiate_person, instantiate_person_with_property_setup, number=N
    )

    reassign_dependee_name_setup = \
        dependee_name_reassignment_setup_template.format(property_args)
    reassign_dependee_name_time = timeit.timeit(
        reassign_name, reassign_dependee_name_setup, number=N
    )

    return (construction_time, instantiation_time, reassign_dependee_name_time)


# Code template strings to be timed for scenario 4

construct_parent_with_property_setup = base_setup \
    + person_construction_template.format(decorator="")
parent_with_property_construction_template = """
class Parent(HasTraits):
    child = Instance(Person)
    a_property = Property({})
"""

parent_with_property_instantiation_setup_template = \
    construct_parent_with_property_setup \
    + parent_with_property_construction_template

child_reassignment_with_property_setup_template = \
    parent_with_property_instantiation_setup_template \
    + "a_parent = Parent(child=Person())"


def scenario4(property_args):
    """ Time the cases described by scenario 4 using the given argument to the
    Property trait defintion.

    Parameters
    ----------
    property_args - Str
        The string defining the argument to be passed in the definition of the
        Property trait.  e.g. "depends_on='child.name'"

    Returns
    -------
    tuple
        A 4-tuple containing the time to construct the HasTraits subclass, the
        time to instantiate it, the time to reassign child, and the time to
        reassign child.name
    """
    construct_parent_with_property_stmt = \
        parent_with_property_construction_template.format(property_args)
    construction_time = timeit.timeit(
        construct_parent_with_property_stmt,
        construct_parent_with_property_setup,
        number=N
    )

    instantiate_parent_with_property_setup = \
        parent_with_property_instantiation_setup_template.format(property_args)
    instantiation_time = timeit.timeit(
        instantiate_parent, instantiate_parent_with_property_setup, number=N
    )

    reassign_child_setup = \
        child_reassignment_with_property_setup_template.format(property_args)
    reassign_child_time = timeit.timeit(
        reassign_child, reassign_child_setup, number=N
    )

    reassign_child_name_time = timeit.timeit(
        reassign_child_name, reassign_child_setup, number=N
    )

    return (
        construction_time,
        instantiation_time,
        reassign_child_time,
        reassign_child_name_time
    )


def report1():
    """ Print a readable benchmark report for scenario 1. """

    print(
        """
    Scenario 1:
        Given a subclass of HasTraits with a trait defined, e.g. name = Str(),
        compare having a method that is decorated with @on_trait_change("name")
        to without. compare having a method that is decorated with
        @observe("name") to without.

        The timing we are interested in:
        (1) Time to import the module, i.e. the class construction.
        (2) Time to instantiate the HasTraits object.
        (3) Time for reassigning the trait to a new value.)
        """
    )
    benchmark_template = "(1): {:.6f}  (2): {:.6f}  (3): {:.6f}"

    print("control -")
    print(benchmark_template.format(*scenario1('')))
    print("on_trait_change('name') -")
    print(benchmark_template.format(*scenario1("@on_trait_change('name')")))
    print("observe('name') - ")
    print(benchmark_template.format(*scenario1("@observe('name')")))
    print("observe(trait('name')) - ")
    print(benchmark_template.format(*scenario1("@observe(trait('name'))")))

    print('-' * 80)


def report2():
    """ Print a readable benchmark report for scenario 2. """

    print(
        """
    Scenario 2
        Given a subclass of HasTraits with a trait referring to an instance of
        HasTraits, e.g. child = Instance(AnotherClass) where AnotherClass has a
        name trait. compare having a method that is decorated with
        @on_trait_change("child.name") to without. compare having a method that
        is decorated with @observe("child.name") to without.

        The timing we are interested in:
        (1) Time to import the module, i.e. the class construction.
        (2) Time to instantiate the HasTraits object.
        (3) Time for reassigning child to a new value.
        (4) Time for reassigning child.name to a new value.
        """
    )
    benchmark_template = "(1): {:.6f}  (2): {:.6f}  (3): {:.6f}  (4): {:.6f}"

    print("control -")
    print(benchmark_template.format(*scenario2('')))
    print("on_trait_change('child.name') -")
    print(benchmark_template.format(
        *scenario2("@on_trait_change('child.name')")))
    print("observe('child.name') - ")
    print(benchmark_template.format(*scenario2("@observe('child.name')")))
    print("observe(trait('child').trait('name')) - ")
    print(benchmark_template.format(
        *scenario2("@observe(trait('child').trait('name'))")))

    print('-' * 80)


def report3():
    """ Print a readable benchmark report for scenario 3. """

    print(
        """
    Scenario 3
        Given a subclass of HasTraits with a trait that is defined as Property
        that depends on a simple trait comparing having the Property to be
        defined as Property(depends_on="name") to without depends_on. comparing
        having the Property to be defined using Property(observe="name") to
        without observe. (Note that this is a feature currently available on
        master only).

        The timing we are interested in:
        (1) Time to import the module, i.e. the class construction.
        (2) Time to instantiate the HasTraits object.
        (3) Time for changing the trait being depended-on / observed.
        """
    )
    benchmark_template = "(1): {:.6f}  (2): {:.6f}  (3): {:.6f}"

    print("control -")
    print(benchmark_template.format(*scenario3('')))
    print("depends_on='name' -")
    print(benchmark_template.format(*scenario3("depends_on='name'")))
    print("observe='name' - ")
    print(benchmark_template.format(*scenario3("observe='name'")))
    print("observe=trait('name') - ")
    print(benchmark_template.format(*scenario3("observe=trait('name')")))

    print('-' * 80)


def report4():
    """ Print a readable benchmark report for scenario 4. """

    print(
        """
    Scenario 4
        Given a subclass of HasTraits with a trait that is defined as Property
        that depends on an extended trait, compare having the Property be
        defined as Property(depends_on="child.name") to without depends_on.
        compare having the Property defined as Property(observe="child.name")
        to without observe. (Note that this is a feature currently available on
        master only).

        The timing we are interested in:
        (1) Time to import the module, i.e. the class construction.
        (2) Time to instantiate the HasTraits object.
        (3) Time for reassigning child to a new value.
        (4) Time for reassigning child.name to a new value.
        """
    )
    benchmark_template = "(1): {:.6f}  (2): {:.6f}  (3): {:.6f}  (4): {:.6f}"

    print("control -")
    print(benchmark_template.format(*scenario4('')))
    print("depends_on='child.name' -")
    print(benchmark_template.format(*scenario4("depends_on='child.name'")))
    print("observe='child.name' - ")
    print(benchmark_template.format(*scenario4("observe='child.name'")))
    print("observe=trait('child').trait('name') - ")
    print(benchmark_template.format(
        *scenario4("observe=trait('child').trait('name')")))

    print('-' * 80)


def main():
    report1()
    report2()
    report3()
    report4()


if __name__ == '__main__':
    main()
