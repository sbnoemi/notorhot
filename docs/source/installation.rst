************************************
Getting Started With django-notorhot
************************************

.. contents:: Table of Contents
   :local:
   :backlinks: top   


Requirements
============

django-notorhot requires Python 2.6 or 2.7 as well as the packages listed below.  It may also work on Python 3.x but has not yet been tested.

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

.. code-block:: bash
   
   pip install -e git+https://github.com/sbnoemi/notorhot.git@0.3#egg=django-notorhot
   
This will automatically install django-notorhot's :ref:`dependencies <dependencies>`.

2. Add the ``sorl.thumbnail``, ``model_utils``, and ``notorhot`` modules to your ``INSTALLED_APPS`` setting:

.. code-block:: python

   # settings.py

   INSTALLED_APPS = (
      ...
      'sorl.thumbnail',
      'model_utils',
      'notorhot',
      ...
   )

3. Update your database by running ``manage.py migrate notorhot`` (if you have South installed) or ``manage.py syncdb`` (if you don't).

4. Add django-notorhot's URLs to your ``urlconf`` (:ref:`see below <setup_views>`).

5. Make sure you have a ``base.html`` template with a ``{% block body %}`` block.  Or :doc:`override the default django-notorhot templates <extending>` to integrate with your project's template structure.

6. Add content (see :doc:`models` documentation).


.. _setup_views:

Hooking Up the Views
====================

django-notorhot comes "out of the box" with usable basic views for selecting competition categories, viewing and voting on competitions, viewing candidate details, and a leaderboard.  To use these views, include django-notorhot's urlconf in your own:

.. code-block:: python

   # urls.py
      
   urlpatterns = patterns('',
      ...
      url(r'any-custom-path/',  include('notorhot.urls')),
      ...
   )

For more complex needs, you can also :doc:`extend django-notorhot's functionality <extending>` with custom templates, models, and/or views.