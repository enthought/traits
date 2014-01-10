:mod:`has_traits` Module
========================

.. automodule:: traits.has_traits
    :no-members:

Classes
-------

.. autoclass:: ViewElement

.. autoclass:: MetaHasTraits

.. autoclass:: MetaInterface

    .. automethod:: __init__

    .. automethod:: __call__

.. autoclass:: MetaHasTraitsObject

    .. automethod:: __init__

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

.. autoclass:: HasPrivateTraits

.. autoclass:: SingletonHasTraits

.. autoclass:: SingletonHasStrictTraits

.. autoclass:: SingletonHasPrivateTraits

.. autoclass:: Vetoable

.. autoclass:: Interface

.. autoclass:: ISerializable

.. autoclass:: traits_super

ABC classes
-----------

.. note:: These classes are only available when the abc module is present.

.. autoclass:: ABCMetaHasTraits

.. autoclass:: ABCHasTraits

.. autoclass:: ABCHasStrictTraits

Functions
---------

.. autofunction:: get_delegate_pattern

.. autofunction:: weak_arg

.. autofunction:: property_depends_on

.. autofunction:: cached_property

.. autofunction:: on_trait_change

.. autofunction:: implements
