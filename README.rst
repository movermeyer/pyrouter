pyrouter
========

.. image:: https://travis-ci.org/felixcarmona/pyrouter.png?branch=master
    :target: https://travis-ci.org/felixcarmona/pyrouter

.. image:: https://coveralls.io/repos/felixcarmona/pyrouter/badge.png?branch=master
    :target: https://coveralls.io/r/felixcarmona/pyrouter?branch=master

.. image:: https://pypip.in/d/pyrouter/badge.png
    :target: https://pypi.python.org/pypi/pyrouter/
    :alt: Downloads

.. image:: https://pypip.in/v/pyrouter/badge.png
    :target: https://pypi.python.org/pypi/pyrouter/
    :alt: Latest Version

Routing in Action
=================
A route is a map from a URL path to a controller.

For example, suppose you want to match any URL like /blog/my-post or /blog/all-about-cats and send it to a
controller that can look up and render that blog entry info. The route is simple:

.. code-block:: python

  ...
  routes = {
      'blog_show': {
          'path':       '/blog/{slug}',
          'methods':    ['GET'],
          'controller': 'myapplication.blog.BlogController'
      }
  }
  ...

The path defined by the ``blog_show`` route acts like ``/blog/*`` where the wildcard is given the name slug.
For the URL ``/blog/my-blog-post``, the slug variable gets a value of ``my-blog-post``,
which is available for you to use in your controller (keep reading). The ``blog_show`` is the internal name of the
route, which doesn't have any meaning yet and just needs to be unique. Later, you'll use it to generate URLs.

The ``controller`` parameter is a special key that tells **pyrouter** which controller should be executed when a URL matches
this route. The ``controller`` string value point to a specific python module > class:

.. code-block:: python
   :linenos:

   # myapplication/blog.py
   from pyhttp import Response


   class BlogController:
       def __init__(request):
          """ @type request: pyhttp.Request """
          self._request = request
          
       def action(self, slug):
           # use the slug variable to query the database
           post_info = ...

           response = Response()

           response.data = post_info

           return response

Congratulations! You've just created your first route and connected it to a controller.
Now, when you visit ``/blog/my-post``, the ``action`` method of the ``myapplication.blog.BlogController`` class will be
executed and the ``slug`` variable will be equal to ``my-post``.

This is the goal of the **pyrouter**: to map the URL of a request to a controller.
Along the way, you'll learn all sorts of tricks that make mapping even the most complex URLs easy.

Customizing the path matching Requirements
------------------------------------------


Creating Routes
===============

Customizing the action method name of the controller class
----------------------------------------------------------

Adding HTTP Method Requirements
-------------------------------
In addition to the URL, you can also match on the *method* of the incoming request (i.e. GET, HEAD, POST, PUT, DELETE).
Suppose you have a contact form with two controllers - one for displaying the form info (on a GET request) and one for
processing the form when it's submitted (on a POST request).
This can be accomplished with the following route configuration:

.. code-block:: python

  ...
  routes = {
      'contact': {
          'path':       '/contact',
          'methods':    ['GET'],
          'controller': 'myapplication.main.ContactController'
      },
      'contact_process': {
          'path':       '/contact',
          'methods':    ['POST'],
          'controller': 'myapplication.main.ContactProcessController'
      }
  }
  ...

Despite the fact that these two routes have identical paths (``/contact``), the first route will match only GET requests
and the second route will match only POST requests. This means that you can display the form info and submit the form
via the same URL, while using distinct controllers for the two actions.

.. note::

    If no method is specified, the route will match with *all* valid methods.

    According to the *RFC 2616*, the valid HTTP request methods are:

    ``GET``, ``HEAD``, ``POST``, ``PUT``, ``DELETE``, ``TRACE``, ``OPTIONS``, ``CONNECT`` and ``PATCH``

.. note::

    You can specify multiples methods specifying a list.

    All of the following method configurations are valid:

    .. code-block:: python

       'methods': ['GET']

    .. code-block:: yaml

       'methods': ['GET', 'POST']


Adding Protocol Requirements to use HTTPS or HTTP
-------------------------------------------------
Sometimes, you want to secure some routes and be sure that they are only accessed via the HTTPS protocol.

This can be accomplished with the following route configuration:

.. code-block:: python

    routes = {
        'contact': {
            'path':       '/contact',
            'controller': 'myapplication.main.ContactController',
            'protocols':  ['https']
        }
    }

.. note::

    If the ``protocols`` directive is not specified, by default the route will match with **HTTP** and **HTTPS**.

.. note::

    The protocols will be specified using a list.

    All of the following method configurations are valid:

    .. code-block:: python

       'protocols': ['http']

    .. code-block:: python

       'protocols': ['http', 'https']


Adding Host Requirements
------------------------

Configuring the Dispatcher
==========================

Controllers Dependencies
------------------------
