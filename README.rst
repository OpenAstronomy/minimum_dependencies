minimum_dependencies
====================

Generate the minimum dependencies for a Python project based on the lower pins.


Installation
************

This package is available on PyPI. You can install it with pip:

.. code-block:: bash

    $ pip install minimum_dependencies


Usage
*****

``minumum_dependencies`` can be used as a command line tool or as a library.

CLI
---

The manpage for the CLI tool is below:

.. code-block:: bash

    $ minimum_dependencies --help
    usage: minimum_deps [-h] [--filename FILENAME] [--extras [EXTRAS ...]] package

    Generate the minimum requirements for a package based on the lower pins of its dependencies.

    positional arguments:
    package               Name of the package to generate requirements for

    options:
    -h, --help            show this help message and exit
    --filename FILENAME, -f FILENAME
                            Name of the file to write out
    --extras [EXTRAS ...], -e [EXTRAS ...]
                            List of optional dependency sets to include

For example, to generate the minimum dependencies for ``requests``:

.. code-block:: console

    $ minimum_dependencies requests
    charset-normalizer==2.0.0
    idna==2.5
    urllib3==1.21.1
    certifi==2017.4.17

Similarly, to generate the minimum dependencies for ``minimum_dependencies`` with all its optional dependencies:

.. code-block:: console

    $ minimum_dependencies minimum_dependencies --extras test other
    importlib-metadata==4.11.4
    packaging==19.0
    requests==2.22.0
    astropy[all]==5.0
    pytest==6.0.0
    pytest-doctestplus==0.12.0

Library Usage
-------------

The library provides two public functions:
    * ``create``: takes a package name and returns a list of requirement strings.
    * ``write``: takes a package name and a filename and writes the requirements to the file.

For example, to generate the minimum dependencies for ``requests``:

.. code:: pycon

    >>> import minimum_dependencies
    >>> minimum_dependencies.create("requests")
    ['charset-normalizer==2.0.0\n', 'idna==2.5\n', 'urllib3==1.21.1\n', 'certifi==2017.4.17\n']
    >>> minimum_dependencies.write(
    ...     "requests", "requirements.txt"
    ... )  # writes the requirements to requirements.txt

One can also pass these methods a list of ``extras`` (optional installs for the package) to
include in the requirements. For example, to generate the minimum dependencies for ``minimum_dependencies``
with all its optional dependencies:

.. code:: pycon

    >>> import minimum_dependencies
    >>> minimum_dependencies.create("minimum_dependencies", extras=["test", "other"])
    ['importlib-metadata==4.11.4\n', 'packaging==19.0\n', 'requests==2.22.0\n', 'astropy[all]==5.0\n', 'pytest==6.0.0\n', 'pytest-doctestplus==0.12.0\n']
    >>> minimum_dependencies.write(
    ...     "minimum_dependencies", "requirements.txt", extras=["test", "other"]
    ... )  # writes the requirements to requirements.txt
