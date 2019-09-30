""" Variants of weak-key dictionaries that are based on object identity.

They will ignore the ``__hash__`` and ``__eq__`` implementations on the
objects. These are intended for various kinds of caches that map instances of
classes to other things without keeping those instances alive. Note that
iteration is not guarded, so if one were iterating over these dictionaries and
one of the weakrefs got cleaned up, this might modify the structure and break
the iteration. As this is not a common use for such caches, we have not
bothered to make these dicts robust to that case.
"""

try:
    # Collections Abstract Base Classes was moved to the collections.abc 
    # module in python 3.3
    # This try expect block can be removed when python 2 support is dropped.
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

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
        return "<WeakIDDict at 0x{0:x}>".format(id(self))

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
