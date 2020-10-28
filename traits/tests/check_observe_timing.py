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

import textwrap
import timeit


# Number of iterations to perform:
N = 10000

# Code template strings to be timed for scenario 1

# General setup not to be included in the timing.
BASE_SETUP = textwrap.dedent("""
    from traits.api import (
        HasTraits, Instance, observe, on_trait_change, Property, Str
    )
    from traits.observation.api import trait
""")

# Construct HasTraits subclass with decorated method
PERSON_CONSTRUCTION_TEMPLATE = textwrap.dedent("""

    class Person(HasTraits):
        name = Str()
        {decorator}
        def some_method(self, event):
            pass

""")

# Instantiate the HasTraits subclass with decorated method
INSTANTIATE_PERSON = textwrap.dedent("""
    a_person = Person()
""")

# Update the trait being observed
REASSIGN_NAME = textwrap.dedent("""
    a_person.name = ''
""")


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
    construct_person = PERSON_CONSTRUCTION_TEMPLATE.format(decorator=decorator)
    construction_time = timeit.timeit(
        stmt=construct_person,
        setup=BASE_SETUP,
        number=N
    )

    instantiation_time = timeit.timeit(
        stmt=INSTANTIATE_PERSON,
        setup=BASE_SETUP + construct_person,
        number=N
    )

    reassign_person_name_time = timeit.timeit(
        stmt=REASSIGN_NAME,
        setup=BASE_SETUP + construct_person + INSTANTIATE_PERSON,
        number=N
    )

    return (construction_time, instantiation_time, reassign_person_name_time)


# Code template strings to be timed for scenario 2

# Setup for constructing subclass of HasTraits with a trait referring to an
# instance of HasTraits
CONSTRUCT_PARENT_SETUP = BASE_SETUP + textwrap.dedent("""

    class Person(HasTraits):
        name = Str()

""")

# Construct subclass of HasTraits with a trait referring to an instance of
# HasTraits with decorated method
PARENT_CONSTRUCTION_TEMPLATE = textwrap.dedent("""

    class Parent(HasTraits):
        child = Instance(Person)
        {decorator}
        def some_method(self, event):
            pass

""")

# Instantiate the class
INSTANTIATE_PARENT = textwrap.dedent("""
    a_parent = Parent(child=Person())
""")

# Update the instance trait containing the trait being observed
REASSIGN_CHILD = textwrap.dedent("""
    a_parent.child = Person()
""")

# Update the trait being observed on the instance trait
REASSIGN_CHILD_NAME = textwrap.dedent("""
    a_parent.child.name = ''
""")


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
    construct_parent = PARENT_CONSTRUCTION_TEMPLATE.format(
        decorator=decorator
    )
    construction_time = timeit.timeit(
        stmt=construct_parent,
        setup=CONSTRUCT_PARENT_SETUP,
        number=N
    )

    instantiation_time = timeit.timeit(
        stmt=INSTANTIATE_PARENT,
        setup=CONSTRUCT_PARENT_SETUP + construct_parent,
        number=N
    )

    reassign_child_time = timeit.timeit(
        stmt=REASSIGN_CHILD,
        setup=CONSTRUCT_PARENT_SETUP + construct_parent + INSTANTIATE_PARENT,
        number=N
    )

    reassign_child_name_time = timeit.timeit(
        stmt=REASSIGN_CHILD_NAME,
        setup=CONSTRUCT_PARENT_SETUP + construct_parent + INSTANTIATE_PARENT,
        number=N
    )

    return (
        construction_time,
        instantiation_time,
        reassign_child_time,
        reassign_child_name_time
    )


# Code template strings to be timed for scenario 3

# Construct subclass of HasTraits with a trait that is defined as Property that
# depends on a simple trait
PERSON_WITH_PROPERTY_CONSTRUCTION_TEMPLATE = textwrap.dedent("""

    class Person(HasTraits):
        name=Str()
        a_property = Property({})

        def _get_a_property(self):
            return self.name

""")


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
        PERSON_WITH_PROPERTY_CONSTRUCTION_TEMPLATE.format(property_args)
    construction_time = timeit.timeit(
        stmt=construct_person_with_property,
        setup=BASE_SETUP,
        number=N
    )

    instantiation_time = timeit.timeit(
        stmt=INSTANTIATE_PERSON,
        setup=BASE_SETUP + construct_person_with_property,
        number=N
    )

    reassign_dependee_name_time = timeit.timeit(
        stmt=REASSIGN_NAME,
        setup=BASE_SETUP + construct_person_with_property + INSTANTIATE_PERSON,
        number=N
    )

    return (construction_time, instantiation_time, reassign_dependee_name_time)


# Code template strings to be timed for scenario 4

# Construct subclass of HasTraits with a trait that is defined as Property that
# depends on an extended trait
PARENT_WITH_PROPERTY_CONSTRUCTION_TEMPLATE = textwrap.dedent("""

    class Parent(HasTraits):
        child = Instance(Person)
        a_property = Property({})

        def _get_a_property(self):
            return self.child.name

""")


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
    construct_parent_with_property = \
        PARENT_WITH_PROPERTY_CONSTRUCTION_TEMPLATE.format(property_args)
    construction_time = timeit.timeit(
        stmt=construct_parent_with_property,
        setup=CONSTRUCT_PARENT_SETUP,
        number=N
    )

    instantiation_time = timeit.timeit(
        stmt=INSTANTIATE_PARENT,
        setup=CONSTRUCT_PARENT_SETUP + construct_parent_with_property,
        number=N
    )

    reassign_child_time = timeit.timeit(
        stmt=REASSIGN_CHILD,
        setup=(
            CONSTRUCT_PARENT_SETUP
            + construct_parent_with_property
            + INSTANTIATE_PARENT
        ),
        number=N
    )

    reassign_child_name_time = timeit.timeit(
        stmt=REASSIGN_CHILD_NAME,
        setup=(
            CONSTRUCT_PARENT_SETUP
            + construct_parent_with_property
            + INSTANTIATE_PARENT
        ),
        number=N
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
        compare having a method with no decorator to one that is decorated with
        @on_trait_change("name"), one decorated with @observe("name"), and one
        with @observe(trait('name')).

        The timing we are interested in:
        (1) Time to import the module, i.e. the class construction.
        (2) Time to instantiate the HasTraits object.
        (3) Time for reassigning the trait to a new value.
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
        name trait, compare having a method with no decorator to one that is
        decorated with @on_trait_change("child.name"), one decorated with
        @observe("child.name"), and one with
        @observe(trait('child').trait('name')).

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
        that depends on a simple trait, compare having the Property be defined
        as Property(), Property(depends_on="name"), Property(observe="name"),
        and Property(observe=trait('name')). (Note that this is a feature
        currently available on master only).

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
        defined as Property(), Property(depends_on="child.name"),
        Property(observe="child.name"), and
        Property(observe=trait('child').trait('name')). (Note that this is a
        feature currently available on master only).

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
