'adaptation' -- Temporary docs
==============================


Introduction
------------

In the adapter pattern, an object is wrapped in a a second object, the
*adapter*, that implements an interface needed by a client.

Adaptation enables a programming style in which each component or service in an
application defines an interface through which it would like to receive
information. When a developer wants to expose a class of objects to
the component, he writes an adapter from the objects original interface to
the target one.

.. image:: adaptation.png

Adaptation allows decoupling the data model from the application components and
services: introducing a new component in the application should not require
modifying the data objects!

In the `adaptation` package, adapters from a protocol (type or interface)
to another can be dynamically registered with a manager object. As components
receive objects, they ask the manager to adapt them to their input
protocol, and use the resulting adapter to extract information from the
object.

The main features of `adaptation` are:

* Support for Python classes, ABCs, and traits `Interface`s

   Protocols can be defined using Python classes, Abstract Base Classes,
   or traits `Interface`s

* Chaining of adapters

   Adapters in `adaptation` can be chained, i.e., an object can be adapted
   to a target protocol as long as there is a sequence of adapters
   that can be used to transform it.

   For example, a `JapanSocket` accepts object implementing the
   `JapanStandard` interface. Two adapters have been registered: one from
   `EUStandard` to `JapanStandard`, and one from `UKStandard` to `EUStandard`.
   The `JapanSocket` can accept a `UKPlug` object implementing the
   `UKStandard` interface, as this can be adapted by chaining the
   UK-to-EU with the EU-to-Japan adapters.

   Chaining is a powerful feature when creating extensible applications.

* Conditional adaptation

* Lazy loading


Resolution order
----------------

The precedence rules.


Examples
--------

Useful examples.


API
---

All the details.


Readings
--------

Recommended readings about adaptation:

* `PyProtocols <http://peak.telecommunity.com/protocol_ref/module-protocols.html>`_,
  a precursor of `adaptation`
* `PEP 246 <http://www.python.org/dev/peps/pep-0246/>`_ on object adaptation
* `Article about adapters in Eclipse plugins
  <http://www.eclipse.org/articles/article.php?file=Article-Adapters/index.html>`_


Roadmap
-------

Once the `adaptation` package has been reviewed and accepted for inclusion in
`traits`, we will start updating `traits` to use it as a replacement for
the `protocols` package. The main `traits` features to revisit in the second
phase are:

1) The "automatic adaptation" feature in `Instance` traits
2) The `Interface` meta class
3) The interface checker

The goal is to remove the `protocols` package in the medium term, which will
simplify and make the code base more robust.

We also would like to consider porting the code using the
`apptools.type_manager` package to `adaptation` and delete the former.


Changelog
---------

2013 Apr : `adaptation` package created
