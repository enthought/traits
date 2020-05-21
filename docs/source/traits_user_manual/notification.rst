Trait Notification
==================

When the value of an attribute changes, other parts of the program might need
to be notified that the change has occurred. The Traits package makes this
possible for trait attributes. This functionality lets you write programs
using the same, powerful event-driven model that is used in writing user
interfaces and for other problem domains.

Traits 6.1 introduces a new API for configuring traits notifications:
|@observe|, which is intended to fully replace an older API using
|@on_trait_change| in order to overcome some of its limitations and flaws.
While |@on_trait_change| is still supported, it may be removed in the future.
See :ref:`on-trait-change-notification` for details on this older API.

.. toctree::
    :maxdepth: 3

    observing.rst

.. toctree::
   :hidden:

   listening.rst

.. |@observe| replace:: :func:`~traits.has_traits.observe`
.. |@on_trait_change| replace:: :func:`~traits.has_traits.on_trait_change`