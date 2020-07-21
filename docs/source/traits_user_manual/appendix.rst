
========
Appendix
========

.. toctree::
   :hidden:

   listening.rst


Trait Notification with **on_trait_change**
--------------------------------------------

See :ref:`on-trait-change-notification` for details on how to set up change
notifications using an older API.


Property **depends_on**
-----------------------

The **depends_on** attribute on a **Property** trait allows change
notifications to be fired for the property when one of its dependents has
changed. This makes use of **on_trait_change** internally and therefore this
is an older API. See :ref:`caching-a-property-value` for the current API.

.. index:: depends_on metadata

For example::

    from traits.api import HasStrictTraits, List, Int, Property

    class TestScores(HasStrictTraits):

        scores = List(Int)
        average = Property(depends_on='scores')

        def _get_average(self):
            s = self.scores
            return (float(reduce(lambda n1, n2: n1 + n2, s, 0)) / len(s))

The **depends_on** metadata attribute accepts extended trait references, using
the same syntax as the on_trait_change() method's name parameter, described in
:ref:`the-name-parameter`. As a result, it can take values that specify
attributes on referenced objects, multiple attributes, or attributes that are
selected based on their metadata attributes.
