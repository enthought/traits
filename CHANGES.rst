Traits CHANGELOG
================

Release 6.2.0
-------------

Released: 2021-01-21

The Traits library is a foundational component of the Enthought Tool Suite. It
provides observable, typed attributes for Python classes, making those classes
suitable for event-driven dataflow programming and for immediate use as models
for graphical user interfaces, like those provided by the TraitsUI library.

Traits 6.2 is the latest feature release in the Traits 6 series, with several
improvements and fixes over Traits 6.1.

Highlights of this release
~~~~~~~~~~~~~~~~~~~~~~~~~~

* The Traits examples are now distributed as part of the Traits egg, and
  are contributed to the ``etsdemo`` application. (The latter can be
  installed from PyPI with ``pip install etsdemo``.)
* Performance of the ``observe`` framework has been significantly improved.
* It's no longer necessary to specify a trait comparison mode of
  ``ComparisonMode.identity`` when using ``observe`` to observe items
  in a ``List``, ``Dict`` or ``Set``.
* Support for Python 3.5 has been dropped.
* When importing from Traits, you should always import from one of the ``api``
  modules (for example, ``traits.api``, ``traits.adaptation.api``, etc.) This
  recommendation has now been made explicit in the documentation. If you find
  something you need that's not available from one of the ``api`` modules,
  please let the Traits developers know.


Detailed PR-by-PR changes
~~~~~~~~~~~~~~~~~~~~~~~~~

More than 60 PRs went into this release. The following people contributed to
this release:

* Aaron Ayres
* Alexandre Chabot-Leclerc
* Kit Choi
* Mark Dickinson
* Kevin Duff
* Glen Granzow
* Matt Hancock
* Rahul Poruri
* Eric Prestat
* Kuya Takami
* Hugo van Kemenade
* Aditya Vats
* Corran Webster


Features
~~~~~~~~

* The ``Property`` trait type now supports the ``observe`` keyword. (#1175,
  #1400)
* Add ``|=`` support to TraitDict for Python 3.9 and later. (#1306)
* Add casting keyword to numeric array types. (#547)
* The Traits examples are now part of the Traits package, and so are
  contributed to ``etsdemo``. (#1275)
* The Traits examples package now includes a beginner's tutorial. (#1061)


Performance
~~~~~~~~~~~

* Parsing of the ``observe`` string was previously a performance bottleneck.
  This has been fixed, by removing some redundant parsing calls and by caching
  parsing results. (#1343, #1344, #1345)


Changes
~~~~~~~

* The ``NoDefaultSpecified`` constant (used as a default value for
  the ``TraitType`` ``default_value`` argument) is now public, made
  available from ``traits.api``. (#1384, #1380, #1378)
* The deprecation of the ``TraitMap`` trait type has been reversed, because
  there are existing uses of ``TraitMap`` that are hard to replace.
  Nevertheless, it is still not recommended to use ``TraitMap`` in new code.
  Use ``Map`` instead. (#1365)
* An attempt to use ``PrefixList`` with an empty list, or ``PrefixMap`` or
  ``Map`` with an empty dictionary, now raises ``ValueError``. As a result,
  the default default value (which used to be ``None``) is always valid.
  (#1351)
* ``TraitListEvent`` arguments are now keyword only. (#1346)
* It's no longer necessary to specify a trait comparison mode of
  ``ComparisonMode.identity`` when using ``observe`` to observe items
  in a ``List``, ``Dict`` or ``Set``. (#1165, #1328, #1240)


Deprecations
~~~~~~~~~~~~

* The ``Function`` and ``Method`` trait types are deprecated. Use
  ``Callable`` or ``Instance`` instead. (#1399, #1397)
* The ``edit`` parameter to ``configure_traits`` has been deprecated. (#1311)
* The ``UnittestTools._catch_warnings`` function has been deprecated. (#1310)
* The use of the ``CHECK_INTERFACES`` global variable for automated
  interface checking has been deprecated. (#1231)


Fixes
~~~~~

* Non-``TraitError`` exceptions raised during ``Tuple`` validation are now
  propagated. Previously they were converted into ``TraitError``. (#1393)
* Dynamic ``Range`` and ``Enum`` traits are now properly validated
  when inside a container (for example ``Tuple`` or ``List``). Previously
  no validation was performed. (#1388, #1392)
* Remove the unused module-level constant ``traits.has_traits.EmptyList``.
  (#1366)
* Don't hard-code class names in ``__repr__`` implementations of
  ``TraitListEvent``, ``TraitSetEvent`` and ``TraitDictEvent``. (#1335)
* Don't notify on empty ``update``\ s of ``Dict`` traits. (#1308)
* Fix exception raised when assigning a NumPy array to a ``List``
  trait. (#1278)
* Fix uses of deprecated ``logger.warn`` function. (#1283)
* Fix a bad ``Instance`` trait declaration for a private trait in
  the ``_TraitChangeCollector`` class. (#1411)


Documentation
~~~~~~~~~~~~~

* Add "Tutorial" section to the main documentation, based on the
  new ``traits.examples`` tutorial content. (#1374)
* Clarify that only the ``api`` modules should be used for imports. (#1387)
* Update copyright header end years. (#1376)
* Update contents of ``image_LICENSE.txt``. (#1362)
* Remove mentions of the removed functions ``adapts`` and ``implements`` from
  the examples and tutorial. (#1367)
* Move Traits introduction description to ``index.rst``. (#1358)
* Fix path to Enthought logo when building docset. (#1285)
* Fix the ``trait_documenter`` extension to be less fragile. (#1247)
* Add user manual documentation for the ``Instance`` trait type. (#1395)
* Document that the ``List``, ``Dict`` and ``Set`` trait types copy on
  assignment. (#1402)
* Various other minor improvements, typo fixes, and other documentation fixes.
  (#1396, #1383, #1381, #1384, #1292, #1355, #1350, #1319, #1292, #1401)


Cleanup and other maintenance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Remove dead code. (#1281)
* Update ``super`` usage to the usual Python 3 argument-less pattern. (#1280)
* Remove per-import ``# noqa`` comments in ``api`` modules in favour of
  per-file ignores in the ``flake8`` configuration. (#1269)
* Remove out-of-date and non-functional coverage badge from README. (#1263)
* Rename ``_i_observable`` module to ``i_observable``. (#1296)
* Refactor and simplify method checks. (#1176)
* Fix typo in optional_dependencies comment. (#1235)
* Use ComparisonMode constants instead of magic numbers. (#1229)


Test suite
~~~~~~~~~~

* Prevent test_enum failures if traitsui or GUI toolkit are not installed.
  (#1349)
* Tests that require ``pkg_resources`` are skipped if ``setuptools`` is not
  installed. (#1301)
* Fix an order-dependency bug in the ``test_subclasses_weakref`` regression
  test. (#1290)
* Fix a typo in a test method name. (#1309)
* Various additional or improved tests for existing code.
  (#1359, #1336, #1330, #1248, #1225, #1208, #1209)


Build and development workflow changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Traits now uses GitHub Actions for continuous integration. The Travis CI
  and Appveyor configurations have been removed. (#1296, #1360)
* CI runs are no longer based on EDM. (#878)
* New CI run for the core test suite, without any optional dependencies.
  (#1314)
* Test Python 3.9 in the continuous integration (and drop tests for Python
  3.5 and older). (#1326, #1313, , #1303)
* Make ``traits.examples`` into a package. (#1348)
* Make examples directories ``flake8``-clean. (#1353)
* Fix examples packaging nit. (#1363)
* Support ``-h`` for getting help in ``etstool.py``. (#1347)
* Add ``shell`` command to ``etstool.py``. (#1293)
* Use the ``flake8_ets`` package in place of the local ``copyright_header``
  package.
  The ``copyright_header`` package has been removed. (#1341)
* Add script ``check_observe_timing.py`` to benchmark performance of
  ``observe`` to compare with ``on_trait_change``. (#1331)
* Correct the minimum Sphinx version in README. (#1216, #1320)
* Restrict Sphinx version to avoid buggy versions. (#1276)
* Make ``mypy`` an optional dependency. (#1289)
* Speed up CI builds for Travis and Appveyor by caching the ``pip`` directory
  (now redundant). (#1241)
* Add automated wheel and sdist building for Traits releases. (#1404, #1291)
* Add cron-job workflow to regularly test install of the latest releases
  from PyPI. (#1406)


Release 6.1.1
-------------

Released: 2020-07-23

Traits 6.1.1 is a bugfix release fixing a handful of minor documentation and
test-related issues with the Traits 6.1.0 release. There are no API-breaking
changes in this release. It's recommended that all users of Traits 6.1.0
upgrade to Traits 6.1.1.

Fixes
~~~~~

* Don't mutate global state at import time in a test module. (#1222)
* Standardize and fix copyright years in source files. (#1227, #1198)
* Fix trait-documenter extension tests for Sphinx 3.1. (#1206)
* Fix trait-documenter extension to handle properties correctly. (#1246)

Documentation fixes
~~~~~~~~~~~~~~~~~~~

* Expand user manual to mention dispatch. (#1195)
* Fix some spelling and grammar errors in the user manual. (#1210)
* Fix description in README to match the one in the setup script. (#1219)
* Update PyPI links and capitalization in README.rst. (#1250)
* Fix user manual mentioning a nonexisting feature in metadata filter. (#1207)
* Fix typo in comment in optional_dependencies. (#1235)


Release 6.1.0
-------------

Released: 2020-06-05

The Traits library is a foundational component of the Enthought Tool Suite. It
provides observable, typed attributes for Python classes, making those classes
suitable for event-driven dataflow programming and for immediate use as models
for graphical user interfaces, like those provided by the TraitsUI library.

Traits 6.1 is the latest feature release in the Traits 6 series, and contains
several major improvements.

Highlights of this release
~~~~~~~~~~~~~~~~~~~~~~~~~~

* A new :mod:`observation <traits.observation>` framework for observing traited
  attributes and other observable objects has been introduced. This is intended
  to provide a full replacement for the existing :func:`on_trait_change`
  mechanism, and aims to fix a number of fundamental flaws and limitations of
  that mechanism. See the :ref:`observe-notification` section of
  the user manual for an introduction to this framework.

* New :class:`~traits.trait_list_object.TraitList`,
  :class:`~traits.trait_dict_object.TraitDict` and
  :class:`~traits.trait_set_object.TraitSet` classes have been added,
  subclassing Python's built-in :class:`python:list`, :class:`python:dict` and
  :class:`python:set` (respectively). Instances of these classes are observable
  objects in their own right, and it's possible to attach observers to them
  directly. These classes were primarily introduced to support the new
  observation framework, and are not expected to be used directly. The API for
  these objects and their notification system is provisional, and may change in
  a future Traits release.

* A new :class:`.Union` trait type has been added. This is intended as a
  simpler replacement for the existing :class:`.Either` trait type, which
  will eventually be deprecated.

* New :class:`.PrefixList`, :class:`.PrefixMap` and :class:`.Map` trait types
  have been added. These replace the existing :class:`.TraitPrefixList`,
  :class:`.TraitPrefixMap` and :class:`.TraitMap` subclasses of
  :class:`.TraitHandler`, which are deprecated.

* Typing stubs for the Traits library have been added in a
  ``traits-stubs`` package, which will be released separately to PyPI. This
  should help support Traits-using projects that want to make use of type
  annotations and type checkers like `mypy <http://mypy-lang.org/>`_.


Notes on upgrading
~~~~~~~~~~~~~~~~~~

As far as possible, Traits 6.1 is backwards compatible with Traits 6.0.
However, there are a few things to be aware of when upgrading.

* Traits 6.1 is not compatible with TraitsUI versions older than TraitsUI 7.0.
  A combination of Traits 6.1 or later with TraitsUI 6.x or earlier will fail
  to properly recognise :class:`~traitsui.view.View` class variables as
  TraitsUI views, and an error will be raised if you attempt to create a
  TraitsUI view.

* Traits now does no logging configuration at all, leaving all such
  configuration to the application.

  In more detail: trait notification handlers should not raise exceptions in
  normal use, so an exception is logged whenever a trait notification handler
  raises. This part of the behaviour has not changed. What *has* changed is the
  way that logged exception is handled under default exception handling.

  Previously, Traits added a :class:`~logging.StreamHandler` to the
  top-level ``"traits"`` logger, so that trait notification exceptions would
  always be visible. Traits also added a :class:`~logging.NullHandler` to that
  logger. Both of those handlers have now been removed. We now rely on
  Python's "handler of last resort", which will continue to make notification
  exceptions to the user visible in the absence of any application-level
  log configuration.

* When listening for changes to the items of a :class:`.List` trait, an index
  or slice set operation no longer performs an equality check between the
  replaced elements and the replacement elements when deciding whether to issue
  a notification; instead, a notification is always issued if at least one
  element was replaced. For example, consider the following class::

    class Selection(HasTraits):
        indices = List(Int)

        @on_trait_change("indices_items")
        def report_change(self, event):
            print("Indices changed: ", event)

  When replacing the `8` with the same integer, we get this behavior::

    >>> selection = Selection(indices=[2, 5, 8])
    >>> selection.indices[2] = 8
    Indices changed:  TraitListEvent(index=2, removed=[8], added=[8])

  Previously, no notification would have been issued.

* The :func:`.Color`, :func:`.RGBColor` and :func:`.Font` trait factories
  have moved to TraitsUI, and should be imported from there rather than from
  Traits. For backwards compatibility, the factories are still
  available in Traits, but they are deprecated and will eventually
  be removed.

* As a reminder, the :data:`.Unicode` and :data:`.Long` trait types are
  deprecated since Traits 6.0. Please replace uses with :class:`.Str` and
  :class:`.Int` respectively. To avoid excessive noise in Traits-using
  projects, Traits does not yet issue deprecation warnings for existing uses of
  :data:`.Unicode` and :data:`.Long`. Those warnings will be introduced in a
  future Traits release, prior to the removal of these trait types.


Pending deprecations
~~~~~~~~~~~~~~~~~~~~

In addition to the deprecations listed in the changelog below, some parts of
the Traits library are not yet formally deprecated, but are likely to be
deprecated before Traits 7.0. Users should be aware of the following possible
future changes:

* The :class:`.Either` trait type will eventually be deprecated. Where
  possible, use :class:`.Union` instead. When replacing uses of
  :class:`.Either` with :class:`.Union`, note that there are some significant
  API and behavioral differences between the two trait types, particularly with
  respect to handling of defaults. See :ref:`migration_either_to_union` for
  more details.

* The ``trait_modified`` event trait that's present on all :class:`.HasTraits`
  subclasses will eventually be removed. Users should not rely on it being
  present in an object's ``class_traits`` dictionary.

* Trait names starting with ``trait``, ``traits``, ``_trait`` or
  ``_traits`` may become reserved for use by ETS at some point in the future.
  Avoid using these names for your own traits.

Detailed PR-by-PR changes
~~~~~~~~~~~~~~~~~~~~~~~~~

More than 160 PRs went into this release. The following people contributed
code changes for this release:

* Ieva Cernyte
* Kit Yan Choi
* Maxime Costalonga
* Mark Dickinson
* Matt Hancock
* Midhun Madhusoodanan
* Shoeb Mohammed
* Franklin Ventura
* Corran Webster

Features
~~~~~~~~

* Add ``os.PathLike`` support for ``Directory`` traits. (#867)
* Add ``Union`` trait type. (#779, #1103, #1107, #1116, #1115)
* Add ``PrefixList`` trait type. (#871, #1142, #1144, #1147)
* Add ``allow_none`` flag for ``Callable`` trait. (#885)
* Add support for type annotation. (#904, #1064)
* Allow mutable values in ``Constant`` trait. (#929)
* Add ``Map`` and ``PrefixMap`` trait types. (#886, #953, #956, #970, #1139,
  #1189)
* Add ``TraitList`` as the base list object that can perform validation
  and emit change notifications. (#912, #981, #984, #989, #999, #1003, #1011,
  #1026, #1009, #1040, #1172, #1173)
* Add ``TraitDict`` as the base dict object that can perform validation and
  emit change notifications. (#913)
* Add ``TraitSet`` as the base set object that can perform validation and
  emit change notifications. (#922, #1043)
* Implement ``observe`` to supersede ``on_trait_change`` for observing trait
  changes. (#976, #1000, #1007, #1065, #1023, #1066, #1070, #1069, #1067,
  #1080, #1082, #1079, #1071, #1072, #1075, #1085, #1089, #1078, #1093, #1086,
  #1077, #1095, #1102, #1108, #1110, #1112, #1117, #1118, #1123, #1125, #1126,
  #1128, #1129, #1135, #1156)

Changes
~~~~~~~

* GUI applications using Traits 6.1 will require TraitsUI >= 7.0. (#1134)
* ``TraitSetEvent`` and ``TraitDictEvent`` initialization arguments are now
  keyword-only. (#1036)
* ``TraitListObject`` will no longer skip notifications even if mutations
  result in content that compares equally to the old values. (#1026)
* ``TraitListEvent.index`` reported by mutations to a list is now normalized.
  (#1009)
* The default notification error handler for Traits no longer configures
  logging, and the top-level ``NullHandler`` log handler has been removed.
  (#1161)

Fixes
~~~~~
* Allow assigning None to ``CTrait.post_setattr``. (#833)
* Fix reference count error. (#907)
* Improve ``HasTraits`` introspection with ``dir()``. (#927)
* Fix the datetime-to-str converters used in ``DatetimeEditor``. (#937)
* Raise ``TraitNotificationError`` on trailing comma in ``on_trait_change``.
  (#926)
* Fix exception swallowing by Trait attribute access. (#959, #960)
* Allow collections in valid values for ``Enum`` trait. (#889)
* Fix ``TraitError`` when mutating a list/dict/set inside another container.
  (#1018)
* Fix setting default values via dynamic default methods or overriding trait in
  subclasses for mapped traits, used by ``Map``, ``Expression``, ``PrefixMap``.
  (#1091, #1188)
* Fix setting default values via dynamic default methods or overriding trait in
  subclasses for ``Expression`` and ``AdaptsTo``. (#1088, #1119, #1152)

Deprecations
~~~~~~~~~~~~

* ``traits.testing.nose_tools`` is deprecated. (#880)
* ``SingletonHasTraits``, ``SingletonHasStrictTraits`` and
  ``SingletonHasPrivateTraits`` are deprecated. (#887)
* ``TraitMap`` is deprecated, use ``Map`` instead. (#974)
* ``TraitPrefixMap`` is deprecated, use ``PrefixMap`` instead. (#974)
* ``TraitPrefixList`` is deprecated, use ``PrefixList``. (#974)
* ``Color``, ``RBGColor`` and ``Font`` are now deprecated. Use the ones from
  TraitsUI instead. (#1022)

Removals
~~~~~~~~

* ``traits_super`` is removed. (#1015)

Documentation
~~~~~~~~~~~~~

* Add details on creating custom trait properties. (#387)
* Cross reference special handler signatures for listening to nested attributes
  in list and dict. (#894)
* Replace 'Traits 5' with 'Traits 6' in the documentation. (#903)
* Use major.minor version in documentation. (#1124)
* Add initial documentation on Traits internals. (#958)
* Fix example class ``OddInt``. (#973)
* Add Dos and Donts for writing change handlers. (#1017)
* Clarify when default initializer is called and when handlers are registered.
  (#1019)
* Fix documentation rendering issues and front matter. (#1039, #1053)
* Clarify when dynamic default values are considered to have existed. (#1068)
* Expand user manual on container traits and objects. (#1058)
* Add intersphinx support to configuration. (#1136)
* Add user manual section on the new ``observe`` notification system. (#1060,
  #1140, #1143)
* Add user manual section on the ``Union`` trait type and how to migrate from
  ``Either`` (#779, #1153, #1162)
* Other minor cleanups and fixes. (#949, #1141, #1178)

Test suite
~~~~~~~~~~

* Allow tests to be skipped if TraitsUI is not installed. (#1038)
* Add ``extras_require`` entry for testing. (#879)
* Add tests for parsing ``on_trait_change`` mini-language. (#921)
* Fix a missing import to allow a test module to be run standalone. (#961)
* Add a GUI test for ``Enum.create_editor``. (#988)
* Fix some module-level ``DeprecationWarning`` messages. (#1157)

Build and continuous integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* CI no longer runs on Python 3.5 (#1044)
* Add configobj dependency and remove remaining 3.5 references in
  ``etstool.py``. (#1051)
* Codecov reports are no longer retrieved for pull requests. (#1109)
* CI tests requiring a GUI are now run against PyQt5 rather than PyQt4.
  (#1127)
* Add Slack notifications for CI. (#1074)
* Fix and improve various ``setup.py`` package metadata fields. (#1185)

Maintenance and code organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Refactor CHasTraits ``traits_inited`` method. (#842)
* Add support for prerelease section in version. (#864)
* Rename comparison mode integer constants in ``ctraits.c``. (#862)
* Follow best practices when opening files. (#872)
* Initialize ``cTrait`` ``getattr``, ``setattr`` handlers in ``tp_new``. (#875)
* Check ``trait_change_notify`` early in ``call_notifiers``. (#917)
* Refactor ``ctraits.c`` for calling trait and object notifiers. (#918)
* ``BaseEnum`` and ``Enum`` fixes and cleanup. (#968)
* Split ``ctraits`` property api to ``_set_property`` and ``_get_property``.
  (#967)
* Fix overcomplicated ``__deepcopy__`` implementation. (#992)
* Add ``__repr__`` implementation for ``TraitListEvent``, ``TraitDictEvent``
  and ``TraitSetEvent``. (#1006, #1148, #1149)
* Remove caching of editor factories. (#1032)
* Remove conditional traitsui imports. (#1033)
* Remove code duplication in ``tutor.py``. (#1034)
* Fix correctness in ``Enum`` default traitsui editor. (#1012)
* Use ``NULL`` for zero-argument ``PyObject_CallMethod`` format. (#1100)
* Miscellaneous other minor fixes, refactorings and cleanups. (#874, #882,
  #915, #920, #923, #924, #935, #939, #944, #950, #964)


Release 6.0.0
-------------

Released: 2020-02-14

No changes since the 6.0.0rc0 release candidate.


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
