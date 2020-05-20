Trait Notification
==================

When the value of an attribute changes, other parts of the program might need
to be notified that the change has occurred. The Traits package makes this
possible for trait attributes. This functionality lets you write programs
using the same, powerful event-driven model that is used in writing user
interfaces and for other problem domains.

Traits 6.1 introduces a new API for configuring traits notifications:
``observe``. The old API using ``on_trait_change`` is still supported, but
it will be deprecated in the future. Prefer ``observe`` to ``on_trait_change``
to remain future proof.

.. toctree::
    :maxdepth: 3

    observing.rst
    listening.rst
