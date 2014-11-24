from unittest import TestCase
from pyrouter.router import Route, Router, generate_routes
from pyhttp import Request


class RouteTestCase(TestCase):
    def test_defaults(self):
        route = Route('foo', 'hello')
        self.assertEqual(route.action, 'action')
        self.assertEqual(route.methods, Route.ALLOWED_METHODS)
        self.assertEqual(route.requirements, {})
        self.assertEqual(route.protocols, ('http', 'https'))
        self.assertEqual(route.host, '.*')

    def test_path(self):
        route = Route('/', 'bar')
        self.assertEqual(route.path, '/')

    def test_methods(self):
        route = Route('foo', 'bar', methods=('GeT',))
        self.assertEqual(('GET',), route.methods)

        route = Route('foo', 'bar', methods=('GET', 'pOsT', 'put'))
        self.assertEqual(('GET', 'POST', 'PUT'), route.methods)

        route.set_methods(('GET',))
        self.assertEqual(('GET',), route.methods)

        route.set_methods(('GET', 'POST'))
        self.assertEqual(('GET', 'POST'), route.methods)

    def test_invalid_methids(self):
        self.assertRaises(Exception, Route, 'foo', 'bar', methods='HELLOWORLD')

    def test_action(self):
        route = Route('foo', 'bar')
        route.set_action('world_action')
        self.assertEqual('world_action', route.action)
        route.set_action('hello')
        self.assertEqual('hello', route.action)

    def test_requirements(self):
        route = Route('foo/{hello}', 'bar')
        route.set_requirements({'hello': '\d+'})
        self.assertEqual({'hello': '(\d+)'}, route.requirements)
        route = Route('foo/{hello}', 'bar')
        route.set_requirements({})
        self.assertEqual({}, route.requirements)

    def test_invalid_requirements(self):
        route = Route('foo/{hello}', 'bar')
        self.assertRaises(Exception, route.set_requirements, ['this is a bad format'])

    def test_protocols(self):
        route = Route('foo', 'bar')
        route.set_protocols(('http',))
        self.assertEqual(route.protocols, ('http',))

    def test_host(self):
        route = Route('foo', 'bar')
        route.set_host('www.example.com')
        self.assertEqual('www.example.com', route.host)


class RouterTestCase(TestCase):
    def test_matching(self):
        request = Request('POST', 'bar', host='example.com', protocol='http')

        route_one = Route('foo/{something}', 'hello', methods=('GET',), requirements={'something': '\d+'})
        route_two = Route('bar', 'world', methods=('POST',), host='(.+\.|)example.com')
        routes = (
            route_one,
            route_two,
        )

        router = Router(routes)
        self.assertTrue(router.match_request(request))

        request = Request('POST', '/foo/bar/test', host='example.com', protocol='http')
        self.assertFalse(router.match_request(request))

        request = Request('GET', '/foo/bar', host='example.com', protocol='http')
        self.assertFalse(router.match_request(request))

        request = Request('POST', 'foo', host='example.com', protocol='http')
        self.assertFalse(router.match_request(request))

    def test_complex_path_matching(self):
        request = Request('POST', 'hello/felix/barcelona/12345678/world', host='example.com', protocol='http')

        route_one = Route('foo', 'hello', methods=('GET',))
        route_two = Route('hello/{name}/{city}/{phone}/world', 'something', methods=('POST',))
        routes = (
            route_one,
            route_two,
        )

        router = Router(routes)
        self.assertTrue(router.match_request(request))


class GenerateRoutesTestCase(TestCase):
    def test_generate_routes(self):
        routes_data = {
            'foo': {
                'methods': ('GET', 'POST'),
                'path': 'test/foo',
                'controller': 'foo.FooController',
                'action': 'other_action',
                'protocols': ('https',)
            },
            'hello': {
                'methods': ('GET',),
                'path': 'test/hello/{amount}',
                'controller': 'foo.HelloController',
                'requirements': {'amount': '(\d+)'},
                'host': 'www.example.com'
            }
        }

        routes = generate_routes(routes_data)
        self.assertEqual(2, len(routes))
