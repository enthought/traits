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
Defines the TraitType class.

The ``TraitType`` class a trait handler that is the base class for modern
traits, and provides a richer API than the old-style traits derived from
``TraitHandler``.
"""

import warnings

from .base_trait_handler import BaseTraitHandler
from .constants import ComparisonMode, DefaultValue, TraitKind
from .trait_base import Missing, Self, TraitsCache, Undefined, class_of
from .trait_dict_object import TraitDictObject
from .trait_errors import TraitError
from .trait_list_object import TraitListObject
from .trait_set_object import TraitSetObject


#: Mapping from trait metadata 'type' to CTrait 'type':
trait_types = {"python": 1, "event": 2}


def _infer_default_value_type(default_value):
    """ Figure out the default value type given a default value.
    """
    if default_value is Missing:
        return DefaultValue.missing
    elif default_value is Self:
        return DefaultValue.object
    elif isinstance(default_value, TraitListObject):
        return DefaultValue.trait_list_object
    elif isinstance(default_value, TraitDictObject):
        return DefaultValue.trait_dict_object
    elif isinstance(default_value, TraitSetObject):
        return DefaultValue.trait_set_object
    elif isinstance(default_value, list):
        return DefaultValue.list_copy
    elif isinstance(default_value, dict):
        return DefaultValue.dict_copy
    else:
        return DefaultValue.constant


def _write_only(object, name):
    """ Raise a trait error for a write-only trait. """
    raise TraitError(
        "The '%s' trait of %s instance is 'write only'."
        % (name, class_of(object))
    )


def _read_only(object, name, value):
    """ Raise a trait error for a read-only trait. """
    raise TraitError(
        "The '%s' trait of %s instance is 'read only'."
        % (name, class_of(object))
    )


class _NoDefaultSpecifiedType(object):
    """
    An instance of this class is used to provide the singleton object
    ``NoDefaultSpecified`` for use in the TraitType constructor.
    """


#: Singleton object that can be passed for the ``default_value`` argument
#: in the :class:`TraitType` constructor, to indicate that no default value
#: was specified.
NoDefaultSpecified = _NoDefaultSpecifiedType()


class TraitType(BaseTraitHandler):
    """ Base class for new trait types.

    This class enables you to define new traits using a class-based
    approach, instead of by calling the Trait() factory function with an
    instance of a TraitHandler derived object.

    When subclassing this class, you can implement one or more of the
    method signatures below. Note that these methods are defined only as
    comments, because the absence of method definitions in the subclass
    definition implicitly provides information about how the trait should
    operate.

    The optional methods are as follows:

    ``get(self, object, name)``

        This is the getter method of a trait that behaves like a property.

        If neither this method nor the ``set()`` method is defined, the value
        of the trait is handled like a normal object attribute. If this
        method is not defined, but the ``set()`` method is defined, the trait
        behaves like a write-only property. This method should return the
        value of the ``name`` property for the ``object`` object.

        Parameters
            object : any
                The object that the property applies to.
            name : str
                The name of the property on ``object``.

    ``set(self, object, name, value)``

        This is the setter method of a trait that behaves like a property.

        If neither this method nor the ``get()`` method is implemented, the
        trait behaves like a normal trait attribute. If this method is not
        defined, but the ``get()`` method is defined, the trait behaves like a
        read-only property. This method does not need to return a value,
        but it should raise a ``TraitError`` exception if the specified
        ``value`` is not valid and cannot be coerced or adapted to a valid
        value.

        Parameters
            object : any
                The object that the property applies to.
            name : str
                The name of the property on ``object``.
            value : any
                The value being assigned as the value of the property.

    ``validate(self, object, name, value)``

        This method validates, coerces, or adapts the specified ``value`` as
        the value of the ``name`` trait of the ``object`` object. This method
        is called when a value is assigned to an object trait that is
        based on this subclass of ``TraitType`` and the class does not
        contain a definition for either the get() or set() methods. This
        method must return the original ``value`` or any suitably coerced or
        adapted value that is a legal value for the trait. If ``value`` is
        not a legal value for the trait, and cannot be coerced or adapted
        to a legal value, the method should either raise a ``TraitError`` or
        call the ``error`` method to raise the ``TraitError`` on its behalf.

    ``is_valid_for(self, value)``

        As an alternative to implementing the ``validate`` method, you can
        instead implement the ``is_valid_for`` method, which receives only
        the ``value`` being assigned. It should return ``True`` if the value is
        valid, and ``False`` otherwise.

    ``value_for ( self, value )``

        As another alternative to implementing the ``validate`` method, you
        can instead implement the ``value_for`` method, which receives only
        the ``value`` being assigned. It should return the validated form of
        ``value`` if it is valid, or raise a ``TraitError`` if the value is not
        valid.

    ``post_setattr(self, object, name, value)``

        This method allows the trait to do additional processing after
        ``value`` has been successfully assigned to the ``name`` trait of the
        ``object`` object. For most traits there is no additional processing
        that needs to be done, and this method need not be defined. It is
        normally used for creating "shadow" (i.e., "mapped" traits), but
        other uses may arise as well. This method does not need to return
        a value, and should normally not raise any exceptions.

    """

    #: The default value for the trait type.
    default_value = Undefined

    #: The metadata for the trait.
    metadata = {}

    def __init__(self, default_value=NoDefaultSpecified, **metadata):
        """ TraitType initializer

        This is the only method normally called directly by client code.
        It defines the trait. The default implementation accepts an optional,
        unvalidated default value, and caller-supplied trait metadata.

        Override this method whenever a different method signature or a
        validated default value is needed.
        """
        if default_value is not NoDefaultSpecified:
            self.default_value = default_value

        if len(metadata) > 0:
            if len(self.metadata) > 0:
                self._metadata = self.metadata.copy()
                self._metadata.update(metadata)
            else:
                self._metadata = metadata
            # By default, private traits are not visible.
            if (
                self._metadata.get("private")
                and self._metadata.get("visible") is None
            ):
                self._metadata["visible"] = False
        else:
            self._metadata = self.metadata.copy()

        self.init()

    def init(self):
        """ Allows the trait to perform any additional initialization needed.
        """
        pass

    def get_default_value(self):
        r""" Get information about the default value.

        The default implementation analyzes the value of the trait's
        ``default_value`` attribute and determines an appropriate
        ``default_value_type`` for the ``default_value``. If you need to
        override this method to provide a different result tuple, the
        following values are valid values for ``default_value_type``:

        - 0, 1: The ``default_value`` item of the tuple is the default
          value.
        - 2: The object containing the trait is the default value.
        - 3: A new copy of the list specified by ``default_value`` is
          the default value.
        - 4: A new copy of the dictionary specified by ``default_value``
          is the default value.
        - 5: A new instance of TraitListObject constructed using the
          ``default_value`` list is the default value.
        - 6: A new instance of TraitDictObject constructed using the
          ``default_value`` dictionary is the default value.
        - 7: ``default_value`` is a tuple of the form:
          ``(callable, args, kw)``, where ``callable`` is a callable,
          ``args`` is a tuple, and ``kw`` is either a dictionary or None.
          The default value is the result obtained by invoking
          ``callable(\*args, \*\*kw)``.
        - 8: ``default_value`` is a callable. The default value is the
          result obtained by invoking ``default_value(object)``, where
          ``object`` is the object containing the trait. If the trait has
          a ``validate()`` method, the ``validate()`` method is also called
          to validate the result.
        - 9: A new instance of ``TraitSetObject`` constructed using the
          ``default_value`` set is the default value.

        Returns
        -------
        default_value_type, default_value : int, any
            The default value information, consisting of an integer, giving
            the type of default value, and the corresponding default value
            as described above.

        """
        dv = self.default_value
        dvt = self.default_value_type
        if dvt < 0:
            dvt = _infer_default_value_type(dv)
            self.default_value_type = dvt

        return (dvt, dv)

    def clone(self, default_value=NoDefaultSpecified, **metadata):
        """ Copy, optionally modifying default value and metadata.

        Clones the contents of this object into a new instance of the same
        class, and then modifies the cloned copy using the specified
        ``default_value`` and ``metadata``. Returns the cloned object as the
        result.

        Note that subclasses can change the signature of this method if
        needed, but should always call the 'super' method if possible.

        Parameters
        ----------
        default_value : any
            The new default value for the trait.
        **metadata : dict
            A dictionary of metadata names and corresponding values as
            arbitrary keyword arguments.

        """
        if "parent" not in metadata:
            metadata["parent"] = self

        new = self.__class__.__new__(self.__class__)
        new_dict = new.__dict__
        new_dict.update(self.__dict__)

        if "editor" in new_dict:
            del new_dict["editor"]

        if "_metadata" in new_dict:
            new._metadata = new._metadata.copy()
        else:
            new._metadata = {}

        new._metadata.update(metadata)

        if default_value is not NoDefaultSpecified:
            new.default_value = default_value
            if self.validate is not None:
                try:
                    new.default_value = self.validate(
                        None, None, default_value
                    )
                except Exception:
                    pass

        return new

    def get_value(self, object, name, trait=None):
        """ Returns the current value of a property-based trait.
        """
        cname = TraitsCache + name
        value = object.__dict__.get(cname, Undefined)
        if value is Undefined:
            if trait is None:
                trait = object.trait(name)

            object.__dict__[cname] = value = trait.default_value_for(
                object, name
            )

        return value

    def set_value(self, object, name, value):
        """ Sets the cached value of a property-based trait and fires the
            appropriate trait change event.
        """
        cname = TraitsCache + name
        old = object.__dict__.get(cname, Undefined)
        if value != old:
            object.__dict__[cname] = value
            object.trait_property_changed(name, old, value)

    # -- Private Methods ------------------------------------------------------

    def __call__(self, *args, **kw):
        """ Allows a derivative trait to be defined from this one.
        """
        return self.clone(*args, **kw).as_ctrait()

    def _is_valid_for(self, object, name, value):
        """ Handles a simplified validator that only returns whether or not the
            original value is valid.
        """
        if self.is_valid_for(value):
            return value

        self.error(object, name, value)

    def _value_for(self, object, name, value):
        """ Handles a simplified validator that only receives the value
            argument.
        """
        try:
            return self.value_for(value)
        except TraitError:
            self.error(object, name, value)

    def as_ctrait(self):
        """ Returns a CTrait corresponding to the trait defined by this class.
        """
        from .traits import CTrait

        metadata = getattr(self, "_metadata", {})
        getter = getattr(self, "get", None)
        setter = getattr(self, "set", None)
        if (getter is not None) or (setter is not None):
            if getter is None:
                getter = _write_only
                metadata.setdefault("transient", True)
            elif setter is None:
                setter = _read_only
                metadata.setdefault("transient", True)
            trait = CTrait(TraitKind.property)
            validate = getattr(self, "validate", None)
            trait.property_fields = (getter, setter, validate)
            metadata.setdefault("type", "property")
        else:
            type = getattr(self, "ctrait_type", None)
            if type is None:
                type = trait_types.get(metadata.get("type"), 0)
            trait = CTrait(type)

            validate = getattr(self, "fast_validate", None)
            if validate is None:
                validate = getattr(self, "validate", None)
                if validate is None:
                    validate = getattr(self, "is_valid_for", None)
                    if validate is not None:
                        validate = self._is_valid_for
                    else:
                        validate = getattr(self, "value_for", None)
                        if validate is not None:
                            validate = self._value_for

            if validate is not None:
                trait.set_validate(validate)

            post_setattr = getattr(self, "post_setattr", None)
            if post_setattr is not None:
                trait.post_setattr = post_setattr
                trait.is_mapped = self.is_mapped

            # Note: The use of 'rich_compare' metadata is deprecated; use
            # 'comparison_mode' metadata instead. Ref: enthought/traits#602.
            rich_compare = metadata.get("rich_compare")
            if rich_compare is not None:
                warnings.warn(
                    "The 'rich_compare' metadata has been deprecated. Please "
                    "use the 'comparison_mode' metadata instead. In a future "
                    "release, rich_compare will have no effect.",
                    DeprecationWarning,
                    stacklevel=6,
                )

                if rich_compare:
                    trait.comparison_mode = ComparisonMode.equality
                else:
                    trait.comparison_mode = ComparisonMode.identity

            comparison_mode = metadata.pop("comparison_mode", None)
            if comparison_mode is not None:
                trait.comparison_mode = comparison_mode

            metadata.setdefault("type", "trait")

        trait.set_default_value(*self.get_default_value())

        trait.handler = self

        trait.__dict__ = metadata.copy()

        return trait

    @classmethod
    def instantiate_and_get_ctrait(cls):
        """ Instantiate the class an return a CTrait instance

        This is primarily to allow traits to be defined within
        classes without having to explicitly call them.
        """
        return cls().as_ctrait()

    def __getattr__(self, name):
        if (name[:2] == "__") and (name[-2:] == "__"):
            raise AttributeError(
                "'%s' object has no attribute '%s'"
                % (self.__class__.__name__, name)
            )

        return getattr(self, "_metadata", {}).get(name, None)
