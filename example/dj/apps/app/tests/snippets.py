import json

from django.utils.encoding import force_text

from germanium.tools import assert_equal
from germanium.test_cases.client import ClientTestCase
from germanium.anotations import data_provider


class SnippetTestCase(ClientTestCase):

    SNIPPET_URL = '/snippet/'
    JSON_SNIPPET_URL = '/json-snippet/'

    def test_return_snippet_content_without_snippet(self):
        resp = self.get(self.SNIPPET_URL)
        assert_equal(
            force_text(resp.content),
            '<div class="snippet snippet-1" data-snippet="test-snippet-1" data-snippet-type="replace">'
            'test-snippet-1-content</div><div class="snippet snippet-2" data-snippet="test-snippet-2" '
            'data-snippet-type="replace">test-snippet-2-content</div>'
        )
        assert_equal(resp['content-type'], 'text/html; charset=utf-8')

    def test_return_json_snippet_content_without_snippet(self):
        resp = self.get(self.JSON_SNIPPET_URL)
        assert_equal(
            force_text(resp.content),
            '<div class="snippet snippet-1" data-snippet="test-snippet-1" data-snippet-type="replace">'
            'test-snippet-1-content</div><div class="snippet snippet-2" data-snippet="test-snippet-2" '
            'data-snippet-type="replace">test-snippet-2-content</div>'
        )
        assert_equal(resp['content-type'], 'text/html; charset=utf-8')

    def test_return_snippet_content_with_snippet(self):
        resp = self.get(self.SNIPPET_URL + '?snippet=test-snippet-1')
        assert_equal(force_text(resp.content), 'test-snippet-1-content')
        assert_equal(resp['content-type'], 'text/html; charset=utf-8')

        resp = self.get(self.SNIPPET_URL + '?snippet=test-snippet-2')
        assert_equal(force_text(resp.content), 'test-snippet-2-content')
        assert_equal(resp['content-type'], 'text/html; charset=utf-8')

        resp = self.get(self.SNIPPET_URL + '?snippet=test-snippet-2&snippet=test-snippet-1')
        assert_equal(force_text(resp.content), 'test-snippet-2-content')
        assert_equal(resp['content-type'], 'text/html; charset=utf-8')

        resp = self.get(self.SNIPPET_URL + '?snippet=test-snippet-1&snippet=test-snippet-2')
        assert_equal(force_text(resp.content), 'test-snippet-1-content')
        assert_equal(resp['content-type'], 'text/html; charset=utf-8')

    def test_return_json_snippet_content_with_snippet(self):
        resp = self.get(self.JSON_SNIPPET_URL + '?snippet=test-snippet-1')
        assert_equal(json.loads(force_text(resp.content)).get('snippets').get('test-snippet-1'),
                     'test-snippet-1-content')
        assert_equal(resp['content-type'], 'text/plain')

        resp = self.get(self.JSON_SNIPPET_URL + '?snippet=test-snippet-2')
        assert_equal(json.loads(force_text(resp.content)).get('snippets').get('test-snippet-2'),
                     'test-snippet-2-content')
        assert_equal(resp['content-type'], 'text/plain')

        resp = self.get(self.JSON_SNIPPET_URL + '?snippet=test-snippet-2&snippet=test-snippet-1')
        assert_equal(json.loads(force_text(resp.content)).get('snippets').get('test-snippet-1'),
                     'test-snippet-1-content')
        assert_equal(json.loads(force_text(resp.content)).get('snippets').get('test-snippet-2'),
                     'test-snippet-2-content')
        assert_equal(resp['content-type'], 'text/plain')

