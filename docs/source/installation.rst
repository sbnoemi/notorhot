************************************
Getting Started With django-notorhot
************************************

.. contents:: Table of Contents
   :local:
   :backlinks: top   


Requirements
============

django-notorhot requires Python 2.6+ as well as the packages listed below.

Additionally, `South <https://pypi.python.org/pypi/South/>`_ is recommended but not required.

`Sphinx <http://sphinx-doc.org/>`_ is required to build the documentation.

.. _dependencies:

Installing django-notorhot (:ref:`see below <installation>`) will automatically install the below packages if they are not already installed:

* `Django <https://www.djangoproject.com/>`_
* `Sorl Thumbnail <https://github.com/mariocesar/sorl-thumbnail>`_
* `Django Model Utils <https://bitbucket.org/carljm/django-model-utils/src>`_
* `PIL <https://pypi.python.org/pypi/PIL>`_ (deprecated) or `Pillow <https://pypi.python.org/pypi/Pillow/>`_ (recommended)
* `django-autoslug <https://pypi.python.org/pypi/django-autoslug>`_


.. _installation: 

Installation
============

.. note:: These instructions assume you are using ``pip`` for Python package management.

1. Install django-notorhot from Github::

.. parsed-literal::
   
   pip install -e git+https://github.com/sbnoemi/notorhot.git@0.2#egg=django-notorhot
   
This will automatically install django-notorhot's :ref:`dependencies <dependencies>`.

2. Add the ``notorhot`` module to your ``INSTALLED_APPS`` setting:

``settings.py``

.. code-block:: python

   INSTALLED_APPS = (
      ...
      'notorhot',
      ...
   )

3. Update your database by running ``manage.py migrate notorhot`` (if you have South installed) or ``manage.py syncdb`` (if you don't).

4. Add django-notorhot's URLs to your ``urlconf`` (:ref:`see below <setup_views>`.

5. Add content (see :doc:`models` documentation).

.. _setup_views::

Hooking Up the Views
====================

Coming soon...

