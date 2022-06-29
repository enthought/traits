"""
A selection of code snippets used to test completeness of the stubs.
"""

from traits.api import HasStrictTraits, Str, TraitError


class HasName(HasStrictTraits):
    name = Str()


def try_assigning_age(x : HasName, new_name : str):
    try:
        x.age = new_name
    except TraitError:
        raise ValueError(f"Bad age: {new_name}")
