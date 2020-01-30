Traits CHANGELOG
================

Release 6.0.0rc0
----------------

Released: 2020-01-30

Release notes
~~~~~~~~~~~~~

Traits 6.0 is a major update to the Traits package, with a number of
backward incompatible changes from its predecessor. Notable changes:

* Python 2.7 is no longer supported; Traits 6.0 requires Python 3.5 or later.
* Trait types related to Python 2 (for example ``Unicode`` and ``Long``) have
  been deprecated in favour of their Python 3 equivalents (for example ``Str``
  and ``Int``).
* Many little-used historical features of Traits have been deprecated, and
  are scheduled for removal in Traits 7.0.
* Some historical features of Traits that had no evidence of external usage
  were removed in Traits 6.0.
* Introspection of ``CTrait`` and ``HasTraits`` objects is greatly improved.
  All of the internal state that was previously hidden within the C extension
  is now accessible from Python.
* The Traits codebase has undergone some significant reorganizations,
  reformattings and style cleanups to make it easier to work with, and
  to improve the separation between Traits and TraitsUI.
* This release was focused mainly on cleanup and bugfixing. Nevertheless,
  it contains a sprinkling of new features. There's a new ``Datetime``
  trait type. The ``Enum`` trait type now supports Python enumerations.
  The ``File`` trait type supports path-like objects.

More than 150 PRs went into this release. The following people contributed
code changes for this release:

* Kit Yan Choi
* Mark Dickinson
* Kevin Duff
* Robert Kern
* Midhun Madhusoodanan
* Shoeb Mohammed
* Sai Rahul Poruri
* Corran Webster
* John Wiggins

Porting guide
~~~~~~~~~~~~~

For the most part, existing code that works with Traits 5.2.0 should
continue to work with Traits 6.0.0 without changes. However, there
are some potentially breaking changes in Traits 6.0.0, and we recommend
applying caution when upgrading.

Here's a guide to dealing with some of the potentially breaking changes.

* The ``Unicode`` and ``CUnicode`` trait types are now simply synonyms for
  ``Str`` and ``CStr``. ``Unicode`` and ``CUnicode`` are considered deprecated.
  For now, no deprecation warning is issued on use of these deprecated trait
  types, but in Traits 6.1.0 and later, warnings may be issued, and in Traits
  7.0.0 these trait types may be removed. It's recommended that users update
  all uses of ``Unicode`` to ``Str`` and ``CUnicode`` to ``CStr`` to avoid
  warnings or errors in the future.

* Similarly, ``Long`` and ``CLong`` are now synonyms for ``Int`` and ``CInt``.
  The same recommendations apply as for the ``Unicode`` / ``Str`` trait types.

* Uses of ``NO_COMPARE``, ``OBJECT_IDENTITY_COMPARE`` and ``RICH_COMPARE``
  should be replaced with the appropriate ``ComparisonMode`` enumeration
  members.

* The validation for a ``Instance(ISomeInterface)`` trait type has changed,
  where ``ISomeInterface`` is a subclass of ``Interface``. Previously, an
  assignment to such a trait validated the type of the assigned value against
  the interface, method by method. Now an ``isinstance`` check is performed
  against the interface instead. Make sure that classes implementing a given
  interface have the appropriate ``provides`` decorator.

  One notable side-effect of the above change is that plain ``mock.Mock``
  instances can no longer be assigned to ``Instance(ISomeInterface)`` traits.
  To get around this, use ``spec=ISomeInterface`` when creating your mock
  object.

  This change does not affect ``Instance`` traits for non-interface classes.

* The format of ``TraitListEvents`` has changed: for list events generated from
  a slice set or slice delete operation where that slice had a step other
  than ``1``, the ``added`` and ``removed`` fields of the event had an extra
  level of list wrapping (for example, ``added`` might be ``[[1, 2, 3]]``
  instead of ``[1, 2, 3]``). In Traits 6.0, this extra wrapping has been
  removed. There may be existing code that special-cased the extra wrapping.

* Many classes and functions have moved around within the Traits codebase.
  If you have code that imports directly from Traits modules and subpackages
  instead of from ``traits.api`` or the other subpackage ``api`` modules, some
  of those imports may fail. To avoid potential for ``ImportError``s, you
  should import from ``traits.api`` whenever possible. If you find yourself
  needing some piece of Traits functionality that isn't exposed in
  ``traits.api``, and you think it should be, please open an issue on the
  Traits bug tracker.

Features
~~~~~~~~

* Add new ``Datetime`` trait type. (#737, #814, #813, #815, #848)
* Support Python Enums as value sets for the ``Enum`` trait. (#685, #828, #855)
* Add ``Subclass`` alias for the ``Type`` trait type. (#739)
* Add path-like support for the ``File`` trait. (#736)
* Add new ``ComparisonMode`` enumeration type to replace the old
  ``NO_COMPARE``, ``OBJECT_IDENTITY_COMPARE`` and ``RICH_COMPARE``
  constants. The old constants are deprecated. (#830, #719, #680)
* Add fast validation for ``Callable`` trait type; introduce
  new ``BaseCallable`` trait type for subclassing purposes.
  (#798, #795, #767)
* Add ``CTrait.comparison_mode`` property to allow inspection and
  modification of a trait's comparison mode. (#758, #735)
* Add ``as_ctrait`` converter function to ``traits.api``. This function
  converts a trait-like object or type to a ``CTrait``, raising ``TypeError``
  for objects that can't be interpreted as a ``CTrait``. It's intended
  for use by users who want to create their own parameterised trait
  types.

  The ``as_ctrait`` feature comes with, and relies upon, a new informal
  interface: objects that can be converted to something of type ``CTrait`` can
  provide an zero-argument ``as_ctrait`` method that returns a new ``CTrait``.
  Types can provide an ``instantiate_and_get_ctrait`` method, which when
  called with no arguments provides a new ``CTrait`` for that type.
  (#783, #794)
* Add a new ``HasTraits._class_traits`` method for introspection of an
  object's class traits. This parallels the existing
  ``HasTraits._instance_traits`` method. This method is intended for use in
  debugging. It's not recommended for users to modify the returned dictionary.
  (#702)
* Add ``CTrait.set_default_value`` method for setting information about the
  default of a ``CTrait``. This provides an alternative to the previous method
  of using ``CTrait.default_value``. The use of ``CTrait.default_value`` to set
  (rather than get) default information is deprecated. (#620)
* Add new methods ``HasTraits._trait_notifications_enabled``,
  ``HasTraits._trait_notifications_vetoed`` to allow introspection of the
  notifications states set by the existing methods
  ``HasTraits._trait_change_notify`` and ``HasTraits._trait_veto_notify``.
  (#704)
* Add ``TraitKind``, ``ValidateTrait`` and ``DefaultValue`` Python enumeration
  types to replace previous uses of magic integers within the Traits codebase.
  (#680, #857)
* The various ``CTrait`` internal flags are now exposed to Python as
  properties: ``CTrait.is_property`` (read-only), ``CTrait.modify_delegate``,
  ``CTrait.setattr_original_value``, ``CTrait.post_setattr_original_value``,
  ``CTrait.is_mapped``, and ``CTrait.comparison_mode``. (#666, #693)

Changes
~~~~~~~

* When pickling a ``CTrait``, the ``py_post_setattr`` and ``py_validate``
  fields are pickled directly. Previously, callables for those fields were
  replaced with a ``-1`` sentinel on pickling. (#780)
* A ``TraitListEvent`` is no longer emitted for a slice deletion which
  doesn't change the contents of the list. (For example, `del obj.mylist[2:]`
  on a list that only has 2 elements.) (#740)
* The ``added`` and ``removed`` attributes on a ``TraitListEvent`` are now
  always lists containing the added or removed elements. Previously, those
  lists were nested inside another list in some cases. (#771)
* Change ``Instance(ISomeInterface)`` to use an ``isinstance`` check on
  trait set instead of using the dynamic interface checker. (#630)
* Create an new ``AbstractViewElement`` abstract base class, and register
  the TraitsUI ``ViewElement`` as implementing it. This paves the way for
  removal of Traits UI imports from Traits. (#617)
* ``ViewElements`` are now computed lazily, instead of at ``HasTraits``
  subclass creation time. This removes a ``traitsui`` import from
  the ``trait.has_traits`` module. (#614)
* The ``traits.util.clean_filename`` utility now uses a different algorithm,
  and should do a better job with accented and Unicode text. (#589)
* Floating-point and integer checks are now more consistent between classes.
  In particular, ``BaseInt`` validation now matches ``Int`` validation, and
  ``Range`` type checks now match those used in ``Int`` and ``Float``. (#588)
* An exception other than ``TraitError`` raised during validation of a
  compound trait will now be propagated. Previously, that exception would
  be swallowed. (#581)
* Traits no longer has a runtime dependency on the ``six`` package. (#638)
* Use pickle protocol 3 instead of pickle protocol 1 when writing pickled
  object state to a file in ``configure_traits``. (#796)
* In ``traits.testing.optional_dependencies``, make sure ``traitsui.api`` is
  available whenever ``traitsui`` is. (#616)
* ``TraitInstance`` now inherits directly from ``TraitHandler`` instead of
  (the now removed) ``ThisClass``. (#761)

Fixes
~~~~~

* Fix a use of the unsupported ``ValidateTrait.int_range``. (#805)
* Remove unnecessary ``copy`` method override from ``TraitSetObject``. (#759)
* Fix ``TraitListObject.clear`` to issue the appropriate items event. (#732)
* Fix confusing error message when ``[None]`` passed into
  ``List(This(allow_none=False))``. (#734)
* Fix name-mangling of double-underscore private methods in classes whose
  name begins with an underscore. (#724)
* Fix ``bytes_editor`` and ``password_editor`` bugs, and add tests for
  all editor factories. (#660)
* Fix coercion fast validation type to do an exact type check instead of
  an instance check. This ensures that instances of subclasses of the
  target type are properly converted to the target type. For example,
  if ``True`` is assigned to a trait of type ``CInt``, the resulting
  value is now ``1``. Previously, it was ``True``. (#647)
* Fix ``BaseRange`` to accept the same values as ``Range``. (#583)
* Fix integer ``Range`` to accept integer-like objects. (#582)
* Fix floating-point ``Range`` to accept float-like values. (#579)
* Fix a missing import in the adaptation benchmark script. (#575)
* Fix issues with the ``filename`` argument to ``configure_traits``. (#572)
* Fix a possible segfault from careless field re-assignments in
  ``ctraits.c``. (#844)

Deprecations
~~~~~~~~~~~~

* The ``NO_COMPARE``, ``OBJECT_IDENTITY_COMPARE`` and ``RICH_COMPARE``
  constants are deprecated. Use the corresponding members of the
  ``ComparisonMode`` enumeration instead. (#719)
* The ``Unicode``, ``CUnicode``, ``BaseUnicode`` and ``BaseCUnicode`` trait
  types are deprecated. Use ``Str``, ``CStr``, ``BaseStr`` and ``BaseCStr``
  instead. (#648)
* The ``Long``, ``CLong``, ``BaseLong`` and ``BaseCLong`` trait types are
  deprecated. Use ``Int``, ``CInt``, ``BaseInt`` and ``BaseCInt`` instead.
  (#645, #573)
* The ``AdaptedTo`` trait type is deprecated. Use ``Supports`` instead. (#760)
* The following trait type aliases are deprecated. See the documentation for
  recommended replacments. ``false``, ``true``, ``undefined``, ``ListInt``,
  ``ListFloat``, ``ListStr``, ``ListUnicode``, ``ListComplex``, ``ListBool``,
  ``ListFunction``, ``ListMethod``, ``ListThis``, ``DictStrAny``,
  ``DictStrStr``, ``DictStrInt``, ``DictStrFloat``, ``DictStrBool``,
  ``DictStrList``. (#627)
* Use of the ``filename`` argument to ``configure_traits`` (for storing
  state to or restoring state from pickle files) is deprecated. (#792)
* The ``TraitTuple``, ``TraitList`` and ``TraitDict`` trait handlers
  are deprecated. Use the ``Tuple``, ``List`` and ``Dict`` trait types instead.
  (#770)
* Use of ``CTrait.default_value`` for setting default value information is
  deprecated. Use ``CTrait.set_default_value`` instead. (#620)
* Use of the ``rich_compare`` trait metadata is deprecated. Use the
  ``comparison_mode`` metadata instead. (#598)

Removals
~~~~~~~~

* Python 2 compatibility support code has been removed. (#638, #644)
* Traits categories have been removed. (#568)
* The following trait handlers have been removed: ``ThisClass``,
  ``TraitClass``, ``TraitExpression``, ``TraitCallable``, ``TraitString``,
  ``TraitRange``, ``TraitWeakRef``. (#782, #711, #699, #698, #625, #593, #587,
  #640)
* ``CTrait.rich_compare`` has been removed. (#598)
* The ``cTrait.cast`` method has been removed. (#663)
* The magical ``TraitValue`` and associated machinery have been removed. (#658)
* The ``Generic`` trait type has been removed. (#657)
* The ``UStr`` trait type and ``HasUniqueStrings`` class have been removed.
  (#654)
* The ``str_find`` and ``str_rfind`` helper functions have been removed. (#633)
* The global ``_trait_notification_handler`` has been removed. (#619)
* ``BaseTraitHandler.repr`` has been removed. (#599)
* ``HasTraits.trait_monitor`` was undocumented, untested, and broken, and
  has been removed. (#570)
* The ``TraitInstance`` trait handler (not to be confused
  with the ``Instance`` trait type) no longer supports adaptation. (#641)
* The ``DynamicView`` and ``HasDynamicViews`` classes have been removed
  from Traits and moved to TraitsUI instead. (#609)
* ``DictStrLong`` has been removed. (#573)

Test suite
~~~~~~~~~~

* Fix various tests to be repeatable. (#802, #729)
* Fix deprecation warnings in the test suite output. (#820, #804, #716)
* Add machinery for testing unpickling of historical pickles. (#787)
* Remove print statements from test suite. (#752, #768)
* Fix a test to clean up the threads it creates. (#731)
* Add tests for extended trait change issues #537 and #538 (#543)
* Other minor test fixes. (#700, #821)

Documentation
~~~~~~~~~~~~~

* Improve documentation of trait container objects. (#810)
* Improve documentation for the ``traits.ctraits`` module. (#826, #824,
  #659, #653, #829, #836)
* Fix badly formatted ``TraitHandler`` documentation. (#817)
* Fix and improve badly formatted trait types documentation. (#843)
* Fix broken module links in section titles in API documentation. (#823)
* Additional class docstring fixes. (#854)
* Add changelog to built documentation, and absorb old changelog into
  the new one. (#800, #799)
* Remove deprecated traits from the user manual. (#656)
* Fix various Sphinx warnings (#717)
* Use SVG badges in README (#567)

Build and continuous integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Enable C asserts in Travis CI runs. (#791)
* Abort CI on compiler warnings in Travis CI runs. (#769)
* Run a ``flake8`` check in both Travis CI and Appveyor runs. (#753, #762)
* Checking copyright statements in Python files as part of CI runs. (#749)
* Turn warnings into errors when building documentation in CI. (#744)
* Add ``gnureadline`` as a development dependency on macOS and Linux. (#607)
* Add an ``etstool.py`` option to run tests quietly. (#606)
* Enable the coverage extension for the documentation build. (#807)
* Remove mocking in documentation configuration, and fix a deprecated
  configuration option. (#696)

Maintenance and code organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This release includes a lot of refactoring and many minor improvements
that will primarily benefit those working with the Traits codebase. These
changes should not affect user-visible functionality. Here's a summary
of the more significant changes.

* A major refactor has removed most of the circular dependencies between
  modules. (#730)
* The codebase is now mostly ``flake8`` clean. (#786, #753, #747, #748, #746,
  #595)
* Copyright headers have been made consistent for all Python files. (#754)
* ``ctraits.c`` has been run through ``clang-tidy`` and ``clang-format`` in
  order to bring it closer to PEP 7 style. (#715)
* Editor factories have been moved into a new ``traits.editor_factories``
  module, to help compartmentalize code dependencies on TraitsUI. (#661)
* Trait container object classes (``TraitDictObject``, ``TraitListObject``,
  ``TraitSetObject``) have each been moved into their own module, along
  with their associated event type. (#677)
* Miscellaneous other minor fixes, refactorings and cleanups.
  (#785, #777, #750, #726, #714, #712, #708, #701, #682, #665, #651,
  #652, #639, #636, #634, #626, #632, #611, #613, #612, #605, #603,
  #600, #597, #586, #585, #584, #580, #577, #578, #564, #806)


Release 5.2.0
-------------

Released: 2019-11-18

Enhancements

* Support installation from source archives. (#528)

Fixes

* Ensure ``TraitListEvent.index`` is always an integer. (#548)
* Update the deprecated ``collections.MutableMapping`` import. (#530)
* Fix inadvertent modification of the ``Category`` base class. (#509)
* Rework version handling in ``setup.py``. (#515)
* Don't autogenerate documentation for ``ViewElement``. (#559)
* Ensure that all tests are ``unittest`` compatible. (#551)

Changes

* Replace occurences of deprecated ``AdaptsTo`` with ``Supports``. (#532)
* Remove ``Class`` trait. (#520)
* Deprecate ``Category`` trait. (#510)
* Fix typos in docstrings. (#502)
* Use decorator form of ``classmethod``. (#500)
* Remove redefinition of ``NullHandler``. (#518)
* Add an import check helper. (#521)
* Clean up Cython tests. (#555)
* Clean up test output. (#553)

Miscellaneous

* Update EDM version on CI to version 2.0.0. (#560)
* Don't finish fast on CI. (#556)
* Use ``unittest`` to run tests in CI. (#552)
* Low-level fixes and style cleanup in ``etstool.py``. (#550)
* Add ``--editable`` option for ``install``, ``update`` CI commands. (#546)
* Make git commit hash available to archives. (#526)
* Fix use of non-edm envs as bootstrap envs on Windows. (#512)
* Remove edm installed package before installing from source. (#516)
* Add help text to click options. (#514)
* Various cleanups, fixes and enhancements in ``etstool.py``. (#511)


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
* Enthought Sphinx Theme for docs (#427)
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


Releases 4.3.0 - 3.6.0
----------------------

Changelogs unavailable.


Release 3.5.0
-------------

Released: 2010-10-15

Enhancements

* adding support for drop-down menu in Button traits, but only for qt backend
* adding 'show_notebook_menu' option to ListEditor so that the user can
  right-click and show or hide the context menu (Qt)
* added selection range traits to make it possible for users to replace
  selected text

Fixes

* fixed null color editor to work with tuples
* bug when opening a view with the ToolbarButton


Release 3.4.0
-------------

Released: 2010-05-26

Enhancements

* adding new example to make testing rgb color editor easier

Fixes

* fixed NumericColumn to not expect object to have model_selection attribute,
  and removed more dead theming code
* fixed API bugs with the NumericColumn where its function signatures
  differed from its base class, but the calling code expected them to all
  be the same
* fixed bug which was related to type name errors caused when running Sphinx
* when using File(exists=True), be sure to validate the type of the value
  first before using os.path.isfile()


Release 3.3.0
-------------

Released: 2010-02-24

Enhancements

The major enhancement this release is that the entire Traits package has been
changed to use relative imports so that it can be installed as a sub-package
inside another larger library or package.  This was not previously possible,
since the various modules inside Traits would import each other directly
through "traits.[module]".  Many thanks to Darren Dale for the
patch.

Fixes

There have been numerous minor bugfixes since the last release.  The most notable
ones are:

* Many fixes involve making Traits UI more robust if wxPython is not installed
  on a system.  In the past, we have been able to use Qt if it was also
  installed, but removing Wx would lead to a variety of little bugs in various
  places.  We've squashed a number of these.  We've also added better checks
  to make sure we're selecting the right toolkit at import and at runtime.
* A nasty cyclic reference was discovered and eliminated in DelegatesTo traits.
* The Undefined and Uninitialized Traits were made into true singletons.
* Much of the inconsistent formatting across the entire Traits source has
  been eliminated and normalized (tabs/spaces, line endings).


Release 3.2.0
-------------

Released: 2009-07-15

Enhancements

* Implemented editable_labels attribute in the TabularEditor for enabling editing of the labels (i.e. the first column)
* Saving/restoring window positions works with multiple displays of different sizes
* New ProgressEditor
* Changed default colors for TableEditor
* Added support for HTMLEditor for QT backend using QtWebKit
* Improved support for opening links in external browser from HTMLEditor
* Added support for TabularEditor for QT backend
* Added support for marking up the CodeEditor, including adding squiggles and dimming lines
* Added SearchEditor
* Improved unicode support
* Changed behavior of RangeEditor text box to not auto-set
* Added support in RangeEditor for specifying the method to evaluate new values.
* Add DefaultOverride editor factory courtesy Stéfan van der Walt
* Removed sys.exit() call from SaveHandler.exit()
