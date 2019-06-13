"""
test_instrumented_iframes.py

Copyright 2019 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
from urlparse import urlparse

from w3af.core.controllers.chrome.tests.helpers import ExtendedHttpRequestHandler
from w3af.core.controllers.chrome.tests.base import BaseInstrumentedUnittest


class TestInstrumentedChromeOneIframe(BaseInstrumentedUnittest):

    def test_load_page_with_iframe(self):
        self._unittest_setup(IframeHandler, load_url=False)
        url = 'http://%s:%s/' % (self.SERVER_HOST, self.server_port)

        self.ic.load_url(url)

        self.ic.wait_for_load()

        self.assertEqual(self.ic.get_dom(), IframeHandler.INDEX)
        self.assertEqual(self.http_traffic_queue.qsize(), 2)

        #
        # The first request / response
        #
        request, response = self.http_traffic_queue.get()

        self.assertEqual(request.get_url().url_string, url)
        self.assertEqual(response.get_url().url_string, url)

        self.assertEqual(response.get_body(), IframeHandler.INDEX)
        self.assertIn('Mozilla/', request.get_headers().get('User-agent'))

        #
        # The second request / response
        #
        request, response = self.http_traffic_queue.get()
        iframe_url = url + 'iframe'

        self.assertEqual(request.get_url().url_string, iframe_url)
        self.assertEqual(response.get_url().url_string, iframe_url)

        self.assertEqual(response.get_body(), IframeHandler.IFRAME)
        self.assertIn('Mozilla/', request.get_headers().get('User-agent'))


class IframeHandler(ExtendedHttpRequestHandler):

    INDEX = ('<html>'
             '<head></head>'
             '<body>Hello world'
             '<iframe src="/iframe"></iframe>'
             '</body>'
             '</html>')

    IFRAME = ('<html>'
              '<head></head>'
              '<body>Inside iframe</body>'
              '</html>')

    def do_GET(self):
        request_path = urlparse(self.path).path

        if request_path == '/':
            code = 200
            body = IframeHandler.INDEX
            headers = {
                'Content-Type': 'text/html',
                'Content-Length': len(body),
                'Content-Encoding': 'identity'
            }

        elif request_path == '/iframe':
            code = 200
            body = IframeHandler.IFRAME
            headers = {
                'Content-Type': 'text/html',
                'Content-Length': len(body),
                'Content-Encoding': 'identity'
            }

        else:
            code = 404
            body = 'Not found'
            headers = {
                'Content-Type': 'text/html',
                'Content-Length': len(body),
                'Content-Encoding': 'identity'
            }

        self.send_response_to_client(code, body, headers)
