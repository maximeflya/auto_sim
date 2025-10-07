Installation
============

Prerequisites
-------------

Tools
~~~~~
python_template_repository requires `Python 3 <https://www.python.org/downloads/>`_.

If you want to install from Github, you need a Github account with read access to
the `python_template_repository <https://github.com/Flyability/python-template-repository>`_ repository.
The installation also requires `git <https://git-scm.com/>`_ and
`SSH setup with your github account <https://docs.github.com/en/authentication/connecting-to-github-with-ssh>`_.

On Ubuntu, you can use the following commands to install ``pip`` and ``git``:

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install python3-pip git


Dependencies
~~~~~~~~~~~~
python_template_repository depends on Flyability packages, which needs to be installed in
your python environment.

You will have to add the URL of the JFrog platform to your pip configuration. Your
``pip.conf`` located in ``~/.pip`` should look like this (if it doesn't exist, you must
create it):

.. code-block:: bash

    [global]
    index-url = https://<username>:<key>@flyability.jfrog.io/artifactory/api/pypi/pypi-virtual/simple

You can refer to this
`documentation <https://flyability.atlassian.net/wiki/spaces/DOQA/pages/2959310849/Binaries+and+packages+management>`_
to know how to retrieve your credentials.


Install from local code
-----------------------

Go at the root of the repository.

It is highly recommended to create a virtual environment before installing the package:

.. code-block:: bash

   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install -U pip setuptools

If you just want to install and use the package, use:

.. code-block:: bash

   python3 -m pip install .

If you want also to develop the project, you may want to install the dev requirements:

.. code-block:: bash

   python3 -m pip install .[dev]

If plan on modifying the code. You can install the package as follows:

.. code-block:: bash

   python3 -m pip install -e .

The ``-e`` option creates a symlink to your local folder, allowing the changes to be used
immediately, without having to reinstall the package.
