from unittest import TestCase
from pyrouter.dispatcher import Dispatcher, DispatcherException
from pyrouter.router import generate_routes
from pyhttp import Request, Response


class HelloController():
    def __init__(self, request, dependency_a, dependency_b):
        self._dependency_a = dependency_a
        self._dependency_b = dependency_b

    def action(self, name, surname):
        response = Response()
        response.data = "%s %s %s %s" % (name, surname, self._dependency_a, self._dependency_b)
        return response


class NodepsController():
    def __init__(self, request):
        pass

    def action(self, name, surname):
        response = Response()
        response.data = "%s %s" % (name, surname)
        return response


class DispatcherTestCase(TestCase):
    def setUp(self):
        routes_data = {
            'hello': {
                'path': '/foo/hello/{name}/{surname}',
                'method': ['GET'],
                'controller': 'pyrouter.tests.test_dispatcher.HelloController'
            },
            'nodeps': {
                'path': '/foo/nodeps/{name}/{surname}',
                'method': ['GET'],
                'controller': 'pyrouter.tests.test_dispatcher.NodepsController'
            },
            'world': {
                'path': '/foo/world/{name}/{number}',
                'methods': ['GET', 'POST'],
                'controller': 'pyrouter.tests.test_dispatcher.WorldController',
                'action': 'world_action',
                'requirements': {
                    'name': '\w+',
                    'number': '\d+'
                },
                'protocols': ['HTTP', 'HTTPS'],
                'host': 'foo.com'
            }
        }

        self._routes = generate_routes(routes_data)

        dependencies = {
            'dependency_a': 12345,
            'dependency_b': 'two'
        }

        self._dispatcher = Dispatcher(self._routes, self._not_found_handler, dependencies)

    def _not_found_handler(self, request, dependency_a, dependency_b):
        """
        @param request: Request
        @return: Response
        """
        return Response('not found', 404)

    def test_dispatch_ok(self):
        request = Request('GET', '/foo/hello/felix/carmona', protocol='http', host='foo.com')
        response = self._dispatcher.dispatch(request)
        self.assertEqual('felix carmona 12345 two', response.get_content())

    def test_dispatch_404(self):
        request = Request('GET', '/x/u/test/xxxx', protocol='http', host='foo.com')
        response = self._dispatcher.dispatch(request)
        self.assertEqual(404, response.get_status_code())

    def test_dispatcher_without_dependencies(self):
        dispatcher = Dispatcher(self._routes, self._not_found_handler)
        request = Request('GET', '/foo/nodeps/felix/carmona', protocol='http', host='foo.com')
        response = dispatcher.dispatch(request)
        self.assertEqual('felix carmona', response.get_content())

    def test_dispatcher_with_list_dependencies(self):
        list_dependencies = [12345, 'two']
        dispatcher = Dispatcher(self._routes, self._not_found_handler, list_dependencies)
        request = Request('GET', '/foo/hello/felix/carmona', protocol='http', host='foo.com')
        response = dispatcher.dispatch(request)
        self.assertEqual('felix carmona 12345 two', response.get_content())

        request = Request('GET', '/x/u/test/xxxx', protocol='http', host='foo.com')
        response = dispatcher.dispatch(request)
        self.assertEqual(404, response.get_status_code())

    def test_dispatcher_with_tuple_dependencies(self):
        list_dependencies = (12345, 'two')
        dispatcher = Dispatcher(self._routes, self._not_found_handler, list_dependencies)
        request = Request('GET', '/foo/hello/felix/carmona', protocol='http', host='foo.com')
        response = dispatcher.dispatch(request)
        self.assertEqual('felix carmona 12345 two', response.get_content())

        request = Request('GET', '/x/u/test/xxxx', protocol='http', host='foo.com')
        response = dispatcher.dispatch(request)
        self.assertEqual(404, response.get_status_code())

    def test_dispatcher_with_invalid_dependencies(self):
        dependencies = 5
        self.assertRaises(DispatcherException, Dispatcher, self._routes, self._not_found_handler, dependencies)
