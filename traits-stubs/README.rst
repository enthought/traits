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


Dependencies
------------

This package depends on Traits_.

.. _Traits: https://pypi.org/project/traits/
.. _mypy: https://pypi.org/project/mypy/
