# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A filter to be used with FilteredTraitObserver for observing traits
with a given metadata. The filter is defined here so that two
observers created using the same parameters compare equally.
"""


class MetadataFilter:
    """ Callable to be used with FilteredTraitObserver for filtering traits
    with the given metadata name.

    This filter returns true if the metadata value is not None, false
    if the metadata is not defined or the value is None.

    Attributes
    ----------
    metadata_name : str
        Name of the metadata to filter traits with.
    """

    __slots__ = ("metadata_name",)

    def __init__(self, metadata_name):
        self.metadata_name = metadata_name

    def __call__(self, name, trait):
        # If the metadata is not defined, CTrait still returns None.
        return getattr(trait, self.metadata_name) is not None

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and self.metadata_name == other.metadata_name
        )

    def __hash__(self):
        return hash((type(self).__name__, self.metadata_name))

    def __repr__(self):
        return (
            "{self.__class__.__name__}"
            "(metadata_name={self.metadata_name!r})".format(self=self)
        )
