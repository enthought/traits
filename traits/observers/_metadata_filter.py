# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A filter to be used with FilteredTraitObserver for observing traits
with a given metadata and value filter. The filter is defined here so that two
observers created using the same parameters compare equally.
"""


class MetadataFilter:
    """ Callable to be used with FilteredTraitObserver for filtering traits
    using defined metadata.

    If the metadata is not defined, the filter will return False.

    Attributes
    ----------
    metadata_name : str
        Name of the metadata to filter traits with.
        If the trait does not have the requested metadata, this filter will
        return false.
    value : callable(value) -> boolean
        The callable must accept a single argument which is
        the metadata value on the trait and return true if the trait
        is to be observed. For removing an existing observer, the ``value``
        callables must compare equally. The callable must be hashable as well.
    """

    def __init__(self, metadata_name, value):
        self.metadata_name = metadata_name
        self.value = value

    def __call__(self, name, trait):
        # hasattr on an CTrait always return true, and the
        # value would be None if it is not defined.
        if self.metadata_name in trait.__dict__:
            value = getattr(trait, self.metadata_name)
            return self.value(value)
        return False

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.metadata_name == other.metadata_name
            and self.value == other.value
        )

    def __hash__(self):
        return hash((type(self).__name__, self.metadata_name, self.value))

    def __repr__(self):
        return "MetadataFilter(metadata_name={!r}, value={})".format(
            self.metadata_name, self.value.__name__
        )
