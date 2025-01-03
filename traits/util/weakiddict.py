# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Variants of weak-key dictionaries that are based on object identity.

They will ignore the ``__hash__`` and ``__eq__`` implementations on the
objects. These are intended for various kinds of caches that map instances of
classes to other things without keeping those instances alive. Note that
iteration is not guarded, so if one were iterating over these dictionaries and
one of the weakrefs got cleaned up, this might modify the structure and break
the iteration. As this is not a common use for such caches, we have not
bothered to make these dicts robust to that case.
"""

from collections.abc import MutableMapping
from weakref import ref


def _remover(key_id, id_dict_ref):
    def callback(wr, id_dict_ref=id_dict_ref):
        id_dict = id_dict_ref()
        if id_dict is not None:
            id_dict.data.pop(key_id, None)

    return callback


class WeakIDDict(MutableMapping):
    """ A weak-key-value dictionary that uses the id() of the key for
    comparisons.
    """

    def __init__(self, dict=None):
        self.data = {}
        if dict is not None:
            self.update(dict)

    def __repr__(self):
        return f"<{self.__class__.__name__} at 0x{id(self):x}>"

    def __delitem__(self, key):
        del self.data[id(key)]

    def __getitem__(self, key):
        return self.data[id(key)][1]()

    def __setitem__(self, key, value):
        self.data[id(key)] = (
            ref(key, _remover(id(key), ref(self))),
            ref(value, _remover(id(key), ref(self))),
        )

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return id(key) in self.data

    def __iter__(self):
        for id_key in self.data:
            wr_key = self.data[id_key][0]
            key = wr_key()
            if key is not None:
                yield key


class WeakIDKeyDict(WeakIDDict):
    """ A weak-key dictionary that uses the id() of the key for comparisons.

    This differs from `WeakIDDict` in that it does not try to make a weakref to
    the values.
    """

    def __getitem__(self, key):
        return self.data[id(key)][1]

    def __setitem__(self, key, value):
        self.data[id(key)] = (ref(key, _remover(id(key), ref(self))), value)
