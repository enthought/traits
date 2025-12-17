.. index:: installation

.. _installation:

============
Installation
============

The latest release of Traits is available from the Python Package Index (PyPI),
and the normal way to install Traits into your Python environment is using
pip::

    python -m pip install traits

Traits includes a C extension module. Binary wheels are provided on PyPI for
common platforms, but some platforms may need to compile Traits from source. On
those platforms, a suitable C compiler will be needed.


Installation from source on macOS
---------------------------------

The system Python 3.8 on macOS Catalina has trouble installing Traits from
source, due to an apparent mismatch in architecture settings. This issue can
be worked around by specifying the "ARCHFLAGS" environment variable for
the install::

    ARCHFLAGS="-arch x86_64" python -m pip install traits

See https://github.com/enthought/traits/issues/1337 for more details.
