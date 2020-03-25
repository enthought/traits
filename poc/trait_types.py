import sys

from traits.constants import ComparisonMode, DefaultValue
from traits.trait_converters import trait_from
from traits.trait_base import SequenceTypes
from traits.trait_type import TraitType
from traits.trait_types import Event

from trait_list_object import TraitListObject, TraitListEvent


class List(TraitType):
    """ A trait type for a list of values of the specified type.

    The length of the list assigned to the trait must be such that::

        minlen <= len(list) <= maxlen

    Parameters
    ----------
    trait : a trait or value that can be converted using trait_from()
        The type of item that the list contains. If not specified, the list
        can contain items of any type.
    value : list
        Default value for the list.
    minlen : integer
        The minimum length of a list that can be assigned to the trait.
    maxlen : integer
        The maximum length of a list that can be assigned to the trait.
    items : bool
        Whether there is a corresponding `<name>_items` trait.
    **metadata
        Trait metadata for the trait.

    Attributes
    ----------
    item_trait : trait
        The type of item that the list contains.
    minlen : integer
        The minimum length of a list that can be assigned to the trait.
    maxlen : integer
        The maximum length of a list that can be assigned to the trait.
    has_items : bool
        Whether there is a corresponding `<name>_items` trait.
    """

    info_trait = None
    default_value_type = DefaultValue.trait_list_object
    _items_event = None

    def __init__(
        self,
        trait=None,
        value=None,
        minlen=0,
        maxlen=sys.maxsize,
        items=True,
        **metadata
    ):
        metadata.setdefault("copy", "deep")

        if isinstance(trait, SequenceTypes):
            trait, value = value, list(trait)

        if value is None:
            value = []

        self.item_trait = trait_from(trait)
        self.minlen = max(0, minlen)
        self.maxlen = max(minlen, maxlen)
        self.has_items = items

        if self.item_trait.instance_handler == "_instance_changed_handler":
            metadata.setdefault("instance_handler", "_list_changed_handler")

        super(List, self).__init__(value, **metadata)

    def validate(self, object, name, value):
        """ Validates that the values is a valid list.

        .. note::

            `object` can be None when validating a default value (see e.g.
            :meth:`~traits.trait_handlers.TraitType.clone`)

        """
        if isinstance(value, list) and (
            self.minlen <= len(value) <= self.maxlen
        ):
            if object is None:
                return value

            return TraitListObject(self, object, name, value)

        self.error(object, name, value)

    def full_info(self, object, name, value):
        """ Returns a description of the trait.
        """
        if self.minlen == 0:
            if self.maxlen == sys.maxsize:
                size = "items"
            else:
                size = "at most %d items" % self.maxlen
        else:
            if self.maxlen == sys.maxsize:
                size = "at least %d items" % self.minlen
            else:
                size = "from %s to %s items" % (self.minlen, self.maxlen)

        return "a list of %s which are %s" % (
            size,
            self.item_trait.full_info(object, name, value),
        )

    def create_editor(self):
        """ Returns the default UI editor for the trait.
        """
        return list_editor(self, self)

    def inner_traits(self):
        """ Returns the *inner trait* (or traits) for this trait.
        """
        return (self.item_trait,)

    # -- Private Methods ------------------------------------------------------

    def items_event(self):
        cls = self.__class__
        if cls._items_event is None:
            cls._items_event = Event(
                TraitListEvent, is_base=False
            ).as_ctrait()

        return cls._items_event

    # ---------------------------
    # Added for observe
    # ---------------------------

    def as_ctrait(self):
        trait = super(List, self).as_ctrait()
        trait.comparison_mode = ComparisonMode.identity
        return trait
