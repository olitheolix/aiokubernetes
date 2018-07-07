========================
Welcome to AIOKUBERNETES
========================

`AsyncIO <https://docs.python.org/3/library/asyncio.html>`_ Kubernetes Client for Python 3.6+.

.. _GitHub: https://github.com/olitheolix/aiokubernetes


Key Features
============

- Based on `aiohttp <https://aiohttp.readthedocs.io/en/stable/>`_.
- Stream output when executing commands in Pods.
- Auto-generated via `Swagger <https://github.com/swagger-api/swagger-codegen>`_
  and `Kubernetes Python client generator <https://github.com/kubernetes-client/gen>`_.


.. _aiokubernetes-installation:

Library Installation
====================

.. code-block:: bash

   $ pip install aiokubernetes

Getting Started
===============

.. literalinclude:: ../examples/list_pods.py

More examples are available `here <github.com/olitheolix/aiokubernetes/examples/>`_.

Source code
===========

The project is hosted on GitHub_

Please feel free to file an issue on the `bug tracker
<https://github.com/olitheolix/aiokubernetes/issues>`_ if you have found a bug
or have some suggestion in order to improve the library.

The library uses `Travis <https://travis-ci.com/olitheolix/aiokubernetes>`_ for
Continuous Integration.


Contributing
============

Feel free to improve this package and send pull requests to GitHub_.


License
=======

The ``aiokubernetes`` package is *Apache 2* licensed and freely available.


Table Of Contents
=================

.. toctree::
   :name: mastertoc
   :maxdepth: 1

   quickstart.rst
   api_reference.rst

