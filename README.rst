###################
Django Not-Or-Hot
###################

Reusable app to build "Hot or Not" / "KittenWar" type websites

Installation
============

We'll package this and release it to PyPi eventually, but for now, use::

   pip install -e git+https://sbnoemi@github.com/sbnoemi/notorhot.git@master#egg=django-notorhot

Configuration
=============

In settings.py, update INSTALLED_APPS to include::

   INSTALLED_APPS = (
      ...
      'model_utils',
      'sorl.thumbnail',
      'notorhot',
      ...
   )

Include django-notorhot's URLs in urls.py::

   urlpatterns = patterns('',
      ...
      url(r'^not-or-hot/',  include('notorhot.urls')),
      ...
   )
   
Populate Categories and Candidates via the admin panel; override templates as needed.


Dependencies
============

django-notorhot requires:

* `Django <https://www.djangoproject.com/>`_
* `Sorl Thumbnail <https://github.com/mariocesar/sorl-thumbnail>`_
* `Django Model Utils <https://bitbucket.org/carljm/django-model-utils/src>`_
* `PIL <https://pypi.python.org/pypi/PIL>`_ (deprecated) or `Pillow <https://pypi.python.org/pypi/Pillow/>`_ (recommended)
* `django-autoslug <https://pypi.python.org/pypi/django-autoslug>`_

Additionally, `South <https://pypi.python.org/pypi/South/>`_ is recommended but not required.


Documentation
=============

Documentation can be built using `Sphinx <http://sphinx-doc.org/>`_.  Please note that there is a bug in Sphinx Autodoc in v1.1 that prevents members of some classes (notably, ``notorhot.contrib.write_in.AbstractFieldTracker``) from being displayed in the documentation.  This bug appears to be fixed in Sphinx v1.2, but as of this writing, Sphinx v1.2 is still in beta.