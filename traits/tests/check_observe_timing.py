# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
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

For details on the varying scenarios see the description strings throughout
the file.

For the original motivation of this script, see the related issue:
enthought/traits#1325
"""

import textwrap
import timeit


# Number of iterations to perform:
N = 10000

DECORATOR_SIMPLE_CASE_DESCRIPTION = """
    Given a subclass of HasTraits with a trait defined, e.g. name = Str(),
    compare having a method with no decorator to one that is decorated with
    @on_trait_change("name"), one decorated with @observe("name"), and one
    with @observe(trait('name')).

    The timing we are interested in:
    (1) Time to import the module, i.e. the class construction.
    (2) Time to instantiate the HasTraits object.
    (3) Time for reassigning the trait to a new value.

    Times are reported as:
    (#): absolute_time  relative_time_to_control
        """

# Code template strings to be timed for the simple decorator case

# General setup not to be included in the timing.
BASE_SETUP = textwrap.dedent("""
    from traits.api import (
        cached_property,
        HasTraits,
        Instance,
        observe,
        on_trait_change,
        Property,
        Str
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
    a_person.name = 'name'
""")


def get_decorated_method_simple_timing(decorator):
    """ Time the cases described by the decorator with simple trait case, using
    the given method decorator.

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


DECORATOR_EXTENDED_CASE_DESCRIPTION = """
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

    Times are reported as:
    (#): absolute_time  relative_time_to_control
        """

# Code template strings to be timed for the decorated method with enxtended
# trait case.

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
    a_parent.child.name = 'name'
""")


def get_decorated_method_extended_timing(decorator):
    """ Time the cases described by the decorated method with enxtended trait
    case, using the given method decorator.

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


PROPERTY_SIMPLE_CASE_DESCRIPTION = """
    Given a subclass of HasTraits with a trait that is defined as Property
    that depends on a simple trait, compare having the Property be defined
    as Property(), Property(depends_on="name"), Property(observe="name"),
    and Property(observe=trait('name')).

    The timing we are interested in:
    (1) Time to import the module, i.e. the class construction.
    (2) Time to instantiate the HasTraits object.
    (3) Time for changing the trait being depended-on / observed.

    Times are reported as:
    (#): absolute_time  relative_time_to_control
        """

CACHED_PROPERTY_SIMPLE_CASE_DESCRIPTION = """
    Identical to the simple property case only using the @chached_property
    decorator on the property's getter method.

    The timing we are interested in:
    (1) Time to import the module, i.e. the class construction.
    (2) Time to instantiate the HasTraits object.
    (3) Time for changing the trait being depended-on / observed.

    Times are reported as:
    (#): absolute_time  relative_time_to_control
        """

# Code template strings to be timed for the (cached) property depending on a
# simple trait scenario.

# Construct subclass of HasTraits with a trait that is defined as Property that
# depends on a simple trait (with option include @cached_property)
PERSON_WITH_PROPERTY_CONSTRUCTION_TEMPLATE = textwrap.dedent("""

    class Person(HasTraits):
        name=Str()
        a_property = Property({})

        {}
        def _get_a_property(self):
            return self.name

""")


def get_property_simple_timing(property_args, cached_property):
    """ Time the cases described by the (cached) property depending on a simple
    trait scenario.  Whether or not the property is cached is based on the
    cached_property argument, and the given property_args argument is used in
    the Property trait defintion.

    Parameters
    ----------
    property_args - Str
        The string defining the argument to be passed in the definition of the
        Property trait.  e.g. "depends_on='name'"
    cached_property - Str
        The string that will be used to decorate the getter method of the
        Property.  Expected to be either '' or '@cached_property'.

    Returns
    -------
    tuple
        A 3-tuple containing the time to construct the HasTraits subclass, the
        time to instantiate it, and the time to reassign the trait being
        depended-on / observed.
    """
    construct_person_with_property = \
        PERSON_WITH_PROPERTY_CONSTRUCTION_TEMPLATE.format(
            property_args,
            cached_property
        )
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


PROPERTY_EXTENDED_CASE_DESCRIPTION = """
    Given a subclass of HasTraits with a trait that is defined as Property
    that depends on an extended trait, compare having the Property be
    defined as Property(), Property(depends_on="child.name"),
    Property(observe="child.name"), and
    Property(observe=trait('child').trait('name')).

    The timing we are interested in:
    (1) Time to import the module, i.e. the class construction.
    (2) Time to instantiate the HasTraits object.
    (3) Time for reassigning child to a new value.
    (4) Time for reassigning child.name to a new value.

    Times are reported as:
    (#): absolute_time  relative_time_to_control
        """

CACHED_PROPERTY_EXTENDED_CASE_DESCRIPTION = """
    Identical to the extended property case only using the @cached_property
    decorator on the property's getter method.

    The timing we are interested in:
    (1) Time to import the module, i.e. the class construction.
    (2) Time to instantiate the HasTraits object.
    (3) Time for reassigning child to a new value.
    (4) Time for reassigning child.name to a new value.

    Times are reported as:
    (#): absolute_time  relative_time_to_control
        """

# Code template strings to be timed for the (cached) property depending on an
# extended trait scenario.

# Construct subclass of HasTraits with a trait that is defined as Property that
# depends on an extended trait (with option to include @cached_property)
PARENT_WITH_PROPERTY_CONSTRUCTION_TEMPLATE = textwrap.dedent("""

    class Parent(HasTraits):
        child = Instance(Person)
        a_property = Property({})

        {}
        def _get_a_property(self):
            return self.child.name

""")


def get_property_extended_timing(property_args, cached_property):
    """ Time the cases described by the (cached) property depending on an
    extended trait scenario. Wether or not the property is cached is determined
    by the cached_property argument, and the given property_args argument is
    used for the Property trait defintion.

    Parameters
    ----------
    property_args - Str
        The string defining the argument to be passed in the definition of the
        Property trait.  e.g. "depends_on='child.name'"
    cached_property - Str
        The string that will be used to decorate the getter method of the
        Property.  Expected to be either '' or '@cached_property'.

    Returns
    -------
    tuple
        A 4-tuple containing the time to construct the HasTraits subclass, the
        time to instantiate it, the time to reassign child, and the time to
        reassign child.name
    """
    construct_parent_with_property = \
        PARENT_WITH_PROPERTY_CONSTRUCTION_TEMPLATE.format(
            property_args,
            cached_property
        )
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


def report(description, benchmark_template, get_time, get_time_args):
    """ Prints a readable benchmark report.

    Parameters
    ----------
    descritption : str
        The description of the benchmarking scenario being reported.
    benchmark_template : str
        The format string used to print the times for the benchmark in a clean,
        formatted way
    get_time : function
        The function used to get the benchmark times for the current benchmark
        scenario
    get_time_args : list of tuples
        The list of tuples containing the arguments to be passed the the
        get_time function.  Note the first argument should give specifics about
        the case being timed and will be printed as part of the report.  e.g.
        ("@observe('name')"), or ("depends_on='name'", '@cached_property').
        The first item in the list will be used as a control.
    """

    print(description)

    control_times = get_time(*get_time_args[0])

    for index, args in enumerate(get_time_args):
        if index == 0:
            print("control -")
            case_times = control_times
        else:
            print(args[0] + ' -')
            case_times = get_time(*args)

        relative_times = map(
            lambda times: times[1] / times[0], zip(control_times, case_times)
        )

        print(benchmark_template.format(*case_times, *relative_times))

    print('-' * 80)


def main():
    BENCHMARK_TEMPLATE_3TIMES = ("(1): {0:.5f} {3:>6.2f} "
                                 "(2): {1:.5f} {4:>6.2f} "
                                 "(3): {2:.5f} {5:>6.2f}")

    BENCHMARK_TEMPLATE_4TIMES = ("(1): {0:.5f} {4:>6.2f} "
                                 "(2): {1:.5f} {5:>6.2f} "
                                 "(3): {2:.5f} {6:>6.2f} "
                                 "(4): {3:.5f} {7:>6.2f}")

    report(
        description=DECORATOR_SIMPLE_CASE_DESCRIPTION,
        benchmark_template=BENCHMARK_TEMPLATE_3TIMES,
        get_time=get_decorated_method_simple_timing,
        get_time_args=[
            ('',),
            ("@on_trait_change('name')",),
            ("@observe('name')",),
            ("@observe(trait('name'))",)
        ]
    )

    report(
        description=DECORATOR_EXTENDED_CASE_DESCRIPTION,
        benchmark_template=BENCHMARK_TEMPLATE_4TIMES,
        get_time=get_decorated_method_extended_timing,
        get_time_args=[
            ('',),
            ("@on_trait_change('child.name')",),
            ("@observe('child.name')",),
            ("@observe(trait('child').trait('name'))",)
        ]
    )

    report(
        description=PROPERTY_SIMPLE_CASE_DESCRIPTION,
        benchmark_template=BENCHMARK_TEMPLATE_3TIMES,
        get_time=get_property_simple_timing,
        get_time_args=[
            ('', ''),
            ("depends_on='name'", ''),
            ("observe='name'", ''),
            ("observe=trait('name')", '')
        ]
    )

    report(
        description=CACHED_PROPERTY_SIMPLE_CASE_DESCRIPTION,
        benchmark_template=BENCHMARK_TEMPLATE_3TIMES,
        get_time=get_property_simple_timing,
        get_time_args=[
            ('', '@cached_property'),
            ("depends_on='name'", '@cached_property'),
            ("observe='name'", '@cached_property'),
            ("observe=trait('name')", '@cached_property')
        ]
    )

    report(
        description=PROPERTY_EXTENDED_CASE_DESCRIPTION,
        benchmark_template=BENCHMARK_TEMPLATE_4TIMES,
        get_time=get_property_extended_timing,
        get_time_args=[
            ('', ''),
            ("depends_on='child.name'", ''),
            ("observe='child.name'", ''),
            ("observe=trait('child').trait('name')", '')
        ]
    )

    report(
        description=CACHED_PROPERTY_EXTENDED_CASE_DESCRIPTION,
        benchmark_template=BENCHMARK_TEMPLATE_4TIMES,
        get_time=get_property_extended_timing,
        get_time_args=[
            ('', '@cached_property'),
            ("depends_on='child.name'", '@cached_property'),
            ("observe='child.name'", '@cached_property'),
            ("observe=trait('child').trait('name')", '@cached_property')
        ]
    )


if __name__ == '__main__':
    main()
