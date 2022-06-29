=========================================
traits-stubs: Type annotations for Traits
=========================================

The *traits-stubs* package contains external type annotations for the Traits_
package. These annotations can be used with static type checkers like mypy_ to
type-check your Traits-using Python code.


Installation
------------
- To install from PyPI, simply use ``pip install traits-stubs``.

- To install from source, run ``pip install .`` from this directory.


Usage
-----
You'll usually want to install mypy_ (or another type checker) into your Python
environment alongside these stubs. You can then use mypy_ from the command
line to check a file or directory, for example with::

    mypy <somefile.py>

Alternatively, some IDEs (including VS Code and PyCharm) can be configured to
perform type checking as you edit.


Development
-----------

To test traits stubs locally:

- Create a fresh venv and activate it, for example with::

  $ python -m venv --clear ~/.venvs/traits-stubs && source ~/.venvs/traits-stubs/bin/activate

- Make sure all build-related packages are up to date

  $ python -m pip install --upgrade pip setuptools wheel

- Install the Traits library into the environment (non-editable install)

  $ python -m pip install .

- Install traits stubs in editable mode (from the repo, not from PyPI).

  $ python -m pip install -e traits-stubs/

- Install mypy (or your favourite type checker)

  $ python -m pip install mypy

- From the traits-stubs directory, run mypy on individual files in
  traits_stubs_tests/examples with e.g.,

  $ python -m mypy traits_stubs_tests/examples/completeness.py

- From the traits-stubs directory, run the test suite with:

  $ python -m unittest discover -v traits_stubs_tests

Note: it's easy to get confusing results if you accidentally use the wrong
version of mypy. To avoid that, you can make sure that you *don't* have mypy
installed globally, and/or always invoke mypy using ``python -m mypy`` from
within the environment.

Note: the unittest run can give the wrong result in the presence of a stale
``.mypy_cache``. If you're getting a pass where you expect to get a failure
(or vice versa), try deleting the local cache and trying again.



Dependencies
------------

This package depends on Traits_.

.. _Traits: https://pypi.org/project/traits/
.. _mypy: https://pypi.org/project/mypy/
