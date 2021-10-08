:mod:`traits.has_traits` Module
===============================

.. automodule:: traits.has_traits
    :no-members:

Classes
-------

.. autoclass:: MetaHasTraits

.. autoclass:: MetaInterface

    .. automethod:: __init__

    .. automethod:: __call__

.. autoclass:: HasTraits
    :exclude-members: wrappers

    .. attribute:: wrappers
        :annotation: =

            | {'same': TraitChangeNotifyWrapper,
            |     'extended': ExtendedTraitChangeNotifyWrapper,
            |     'new': NewTraitChangeNotifyWrapper,
            |     'fast_ui': FastUITraitChangeNotifyWrapper,
            |     'ui': FastUITraitChangeNotifyWrapper}

        Mapping from dispatch type to notification wrapper class type

.. autoclass:: HasStrictTraits

.. autoclass:: HasRequiredTraits

.. autoclass:: HasPrivateTraits

.. autoclass:: Vetoable

.. autoclass:: Interface

.. autoclass:: ISerializable

ABC classes
-----------

.. note:: These classes are only available when the abc module is present.

.. autoclass:: ABCMetaHasTraits

.. autoclass:: ABCHasTraits

.. autoclass:: ABCHasStrictTraits

Functions
---------

.. autofunction:: cached_property

.. autofunction:: get_delegate_pattern

.. autofunction:: observe

.. autofunction:: on_trait_change

.. autofunction:: property_depends_on

.. autofunction:: provides

.. autofunction:: weak_arg

Deprecated Classes
------------------

The following :class:`~.HasTraits` subclasses are deprecated,
and may be removed in a future version of Traits.

.. autoclass:: SingletonHasTraits

.. autoclass:: SingletonHasStrictTraits

.. autoclass:: SingletonHasPrivateTraits

