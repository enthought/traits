=========================================
traits-stubs: Type annotations for Traits
=========================================

This package contains stub files which are type annotations for the most
commonly used classes in the Traits package.

Type annotations are used by static type checkers
to find common bugs without running the program. These merely recommend
and does not enforce changes to the source code for api compatibility.

These annotations have been tested with the `mypy` static type checker.

Information on how to setup and run `mypy` can be found here:

- Repository & Quickstart: https://github.com/python/mypy
- Documentation: https://mypy.readthedocs.io/en/stable/index.html


Installation
------------
- Activate an environment with `traits` installed.
- Install mypy by following the instructions found in the links above.
- Run `pip install .` inside the dirctory /traits-stubs.
- Run `mypy` with `mypy <somefile.py>`.

Note: `mypy` creates a `.mypy_cache` folder when run. This may be excluded
from source control.

Plugins
-------
The recommended way to use `mypy` is by installing the plugin for your favourite
editor. Some plugins call out errors as the files are being modified which can
be very useful.

Here are some plugins that you may want to try:

- PyCharm:
    - Mypy ​(Official)​: https://plugins.jetbrains.com/plugin/13348-mypy-official
    - Mypy (More Popular): https://plugins.jetbrains.com/plugin/11086-mypy

- Visual Studio Code:
    - Mypy: https://marketplace.visualstudio.com/items?itemName=matangover.mypy



Dependencies
------------

* `Traits <https://github.com/enthought/traits>`_
* `mypy <https://github.com/python/mypy>`_

