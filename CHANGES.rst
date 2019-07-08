Traits CHANGELOG
================

Release 5.1.2
-------------

Released: 2019-07-08

Fixes

* Traits documenter no longer generates bad reST for traits whose definition
  spans multiple source lines. (#494)


Release 5.1.1
-------------

Released: 2019-04-18

Fixes

* Revert a change (#449) which accidentally broke external uses of
  ``_py2to3.str_find`` and ``_py2to3.str_rfind``. (#472)

Release 5.1.0
-------------

Released: 2019-04-15

Enhancements

* Make UUID trait initializable. (#459)
* Change default ``FileEditor`` behavior for a ``File`` trait based on
  whether ``exists=True`` is specified for that trait. (#451, #467)

Changes

* The changes made in #373 to make dynamically-added traits pickleable have
  been reverted. (#462)
* ``traits.api.python_version`` has been removed. Internals have been
  refactored to use ``six.PY2`` in preference to ``sys.version_info``.
  (#449)
* Don't depend on the 3rd party ``mock`` library on Python 3; use
  ``unittest.mock`` instead. (#446)

Fixes

* Fix a fragile NumPy-related test that failed (``RuntimeError: empty_like
  method already has a docstring``) with the newest version of NumPy.
  (#443)

Miscellaneous

* ``traits._version.git_revision`` now gives the full commit hash (for local
  builds) instead of an abbreviated 7 hex-digit version. (#453)
* Fix copyright years in documentation build. (#445)
* Rename ``README.txt`` to ``README.rst``, so that GitHub renders it nicely.
* Code cleanups: remove "EOF" markers from code. Remove ``__main__`` blocks
  for unit tests. Remove imports of ``unittest`` from ``unittest_tools``.
  (#448, #446)
* Update Travis CI and Appveyor configurations to run tests against
  all PR branches, not just PRs against master. (#466)


Release 5.0.0
-------------

Released : 30 January 2019

This major release accumulates more than an year's worth of improvements,
changes and bug fixes to the code base.

A few highlights of this release are :

* Removal of 2to3 fixers and the use of six to provide Python 2/3 compatibility
* Removal of deprecated ``traits.protocols`` submodule and related utils.
* New ``HasRequiredTraits`` class
* Better IPython tab completion for ``HasTraits`` subclasses

Changes summary since 4.6.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enhancements

* CI for documentation (#431)
* Remove 2to3 fixers (#430)
* Enthought Sphinx theme for docs (#427)
* New ``HasRequiredTraits`` class (#419)
* Free ``HasTraits`` subclasses from hashing/comparing by identity (#410)
* Unify and fix default list editors (#396)
* Add ``__dir__`` method to ``HasTraits`` for IPython tab completion (#382)
* Python 3 compatibility fixes (#374)
* New context manager for setting trait-change-event tracer (#365)
* Default trait type constants (#354)

Changes

* Remove deprecated ``traits.protocols`` submodule and related utils (#435)
* Fix invalid string escapes (#429)
* Apply the "black" code reformatting utility on the Traits codebase (#432)
* Update CI to use edm and etstool module (#420)
* Clean up ``Float`` and ``BaseFloat`` validation (#393)
* Merge master into Cython port (#370)
* Docs and minor refactoring of ``MetaHasTraits`` class (#366)
* Remove ridiculous premature optimization (#362)
* Add support for PyInstaller app bundler (#361)
* Add description and example for ``Either`` trait type (#360)
* Drop support for Python 2.6 and Python < 3.4 (#345)
* Add make target for docset to be used with Dash/Zeal (#180)

Fixes

* Fix odd error message and wrong exception type (#426)
* Fix Color and RGBColor doc strings (#417)
* Fix use of deprecared ``inspect.getargspec`` function (#408)
* Fix extended names in ``on_trait_change`` lists (#404)
* Support Unicode on trait documenter on Python 2.7 (#386)
* Clear exception from Numpy properly (#377)
* Fix pickling and deepcopying bug with dynamically added traits (#373)
* Set ``auto_set/enter_set`` default once (#371)
* Fix validation of ``This`` trait (#353)
* Make ``cTrait.default_value_for`` raise a ``ValueError`` instead of
  seg faulting when asked for the default value of a trait that doesn't
  have one. (#350)
* Fix misuse of ``unittest.expectedFailure`` decorator (#346)
* Fix issue with overridden ``HasTraits.trait`` function (#343)


Release 4.6.0
-------------

This is an incremental release over 4.5, accumulating over a year's worth of
bugfixes and small improvements to the code.

Highlights of this release include:

* support for Python 3.4 and 3.5.
* new Bytes and ValidatedTuple traits.
* a new ArrayOrNone trait which correctly handles None comparisons with Numpy
  arrays.
* clean-up of the ETSConfig code for TraitsUI toolkit selection.
* better compatibility with NumPy scalar types.
* many other bugfixes and improvements.

Change summary since 4.5.0
~~~~~~~~~~~~~~~~~~~~~~~~~~

Enhancements

* Added a ``Bytes`` Trait and related traits (#329)
* Added support for finding resources from zipped Python source code (#316)
* Added in-place set arithmetic operations for ``TraitSetObject``s and accept
  match behaviour of ``TraitSetObject`` with regular Python sets when
  performing operations with non-set types (eg. lists, dictionaries) (#289)
* Added a context manager to allow provisional selection of a toolkit to
  ``ETSConfig`` (this generally improves reliability of toolkit selection
  for Pyface and TraitsUI). (#276)
* Added Trait change recorder to aid in debugging event-driven code. (#139)
* ``__iadd__`` and ``__imul__`` implemented on TraitListObjects. (#165)
* Added new ``ArrayOrNone`` trait type to replace the
  ``Either(None, Array)`` idiom.  The old idiom results in warnings
  on NumPy >= 1.9. (#219)
* Added a new ``ValidatedTuple`` trait that supports custom validation. (#205)

Changes

* Removed redundant, internal ``ETSConfig`` from Traits codebase. (#327)
* Better error reporting for failed attribute access. (#243)
* Removed buggy ``-toolkit`` commandline option ``ETSConfig``. (#326)
* Removed buggy ``*names`` positional arguments from ``on_trait_change``
  decorator in improved argument passing (#207).
* Allow ``Float`` and ``BaseFloat`` traits to accept Python longs. (#272)
* Clean-up and fixes to example code. (#126)
* Remove outdated ``ImportSpy`` and ``ImportManager`` utilities. (#188)
* The ``deprecated`` decorator now issues a DeprecationWarning (using
  the Python ``warnings`` module) rather than logging a warning via
  the ``logging`` machinery.  It no longer tries to remember when
  a warning has been previously issued. (#220)
* Deprecated ``HasTraits.get()`` and ``HasTraits.set()`` (#190).
* The default ``View`` shows all (non-event) traits whose ``visible`` property
  is not ``False``. Private traits are set ``visible=False`` by default. (#234)

Fixes

* Fix Bool traits so that value stored is always a Python ``bool`` (and in
  particular, not a NumPy ``np.bool_``). (#318)
* Fix Bool traits so that regular validator accepts NumpPy's ``np.bool_``
  boolean values (bringing it in agreement with the fast validator). (#302)
* Fix use of ``next`` in ``TraitDocumenter`` for Python 3 compatibility. (#293)
* Fix off-by-one error when ``TraitListObject`` is setting or deleting slices.
  (#283)
* Fix reference cycles caused by ``sync_traits``. (#135)
* Fix so that ``sys.exc_info()`` works as expected in exception handlers in
  Python 3 (#266)
* Fix ``String`` trait to accept ``str`` subclasses (like ``numpy.str_``).
  (#267)
* Fixed incorrect in list events for ``insert`` operations with an index
  outside the range [``-len(target_list)``, ``len(target_list)``]. (#165)
* Fix incorrect behaviour of ``check_implements`` for overridden methods.
  (#192)
* Fix error when trying to listen to traits using list bracket notation. (#195)
* Fix reference leak in ``CHasTraits._notifiers``. (#248)
* Fix reference leak from use of ``DelegatesTo``. (#260)
* Instance traits weren't included in the result of ``traits()``. (#234)


Release 4.5.0
-------------

Traits is now compatible with Python 3! The library now supports
Python 3.2 and 3.3.

The release also includes increased code coverage and automatic
coverage report through coveralls.io.


Change summary since 4.4.0
~~~~~~~~~~~~~~~~~~~~~~~~~~

Enhancements

* Test files cleanups (#108, #111, #121)
* Add automatic coverage reports (#110, #122)
* Removed obsolete code (#109, #112, #113)
* Increased test coverage (#114, #118)
* Python 3 support (#115).  Thanks Yves Delley.
* Allow setting and resetting the global adaptation manager (#145)
* Various documentation improvements (#132, #133, #148, #154).

Changes

* The Int trait type now accepts Python ints *and* Python longs, as well as
  instances of any Python type that implements the ``__index__`` method.
  Previously, long instances were not accepted. (#104, #123).

Fixes

* Fix crash when trying to validate a property that has been deleted. (#138)
* Fix clearing exception when raising a TraitError (#119)
* Fix automatic adaptation when assigning to List trait (#147)
* Fix some ctraits refcounting and exception clearing bugs (#48).  Thanks Yves
  Delley.


Release 4.4.0
-------------

The major new feature in this release is a new adaptation mechanism in the
``traits.adaptation`` package.  The new mechanism is intended to replace the
older traits.protocols package.  Code written against ``traits.protocols`` will
continue to work, although the ``traits.protocols`` API has been deprecated,
and a warning will be logged on first use of ``traits.protocols``.  See the
'Advanced Topics' section of the user manual for more details.

The release also includes improved support for using Cython with ``HasTraits``
classes, some new helper utilities for writing unit tests for Traits events,
and a variety of bug fixes, stability enhancements, and internal code
improvements.


Change summary since 4.3.0
~~~~~~~~~~~~~~~~~~~~~~~~~~

New features

* The adaptation mechanism in Traits, formerly based on the 'traits.protocols'
  package, has been replaced with the more robust 'traits.adaptation'
  package. (#51)
* Added utility function for importing symbols (name, classes, functions)
  by name: 'traits.util.api.import_symbol'. (#51)
* Users can set a global tracer, which receives all traits change events:
  ``traits.trait_notifiers.set_change_event_tracers``. (#79)

Enhancements

* Update benchmark script. (#54)
* traits.util.deprecated: use module logger instead of root logger. (#59)
* Provide an informative message in AdaptationError. (#62)
* Allow HasTraits classes to be cythonized. (#73)
* Improve tests for cythonization support. (#75)
* Extending various trait testing helpers (#53)

Refactoring

* The Traits notification code has been reworked to remove code duplication,
  and test coverage of that code has been significantly improved. (#79)

Fixes

* Fix race condition when removing a traits listener. (#57)
* Fix ugly interaction between DelegatesTo change handlers, dynamic change
  handlers and two levels of dynamic intialization. (#63)
* Use a NullHandler for all 'traits' loggers. (#64)
* Fix race condition in TraitChangeNotifyWrapper.listener_deleted (#66)
* Fix leaking notifiers. (#68)
* Fix failing special instance trait events. (#78)
* Fix hiding KeyError exception inside trait default initialize method.
  (#81)
* Fix Adapter object initialization. (#93)
* Fix cyclic garbage arising from use of the WeakRef trait type. (#95)
* ``TraitSetObject.copy`` now returns a plain rather than an
  uninitialized ``TraitSetObject`` instance. (#97)
* Fix cyclic garbage arising from dynamic trait change handlers. (#101)
