=============================
swagger_utils
=============================

.. image:: https://badge.fury.io/py/django-swagger-utils.png
    :target: https://badge.fury.io/py/django-swagger-utils

.. image:: https://travis-ci.org/eldos-dl/django-swagger-utils.png?branch=master
    :target: https://travis-ci.org/eldos-dl/django-swagger-utils

Automate API generation from swagger

Documentation
-------------

The full documentation is at https://django-swagger-utils.readthedocs.org.

Quickstart
----------

Install django_swagger_utils::

    pip install django-swagger-utils

Then use it in a project::

    import django_swagger_utils

Features
--------

* TODO

Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements_test.txt
    (myenv) $ python runtests.py

Credits
---------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage

Features
---------

* CUSTOM_SCOPES_CHECK_FUNCTION

::
    Configure CUSTOM_SCOPES_CHECK_FUNCTION with path to a function
    Function should take user and custom_scopes as its arguments
    Ex:
    def custom_scope_check(user, custom_scopes):
        # Write your custom scope check logic
        return
