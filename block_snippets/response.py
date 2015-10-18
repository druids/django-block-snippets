from __future__ import unicode_literals

import json

from django.template.response import TemplateResponse
from django.template.context import make_context, _current_app_undefined

from block_snippets.utils import clean_html


class SnippetsTemplateResponse(TemplateResponse):

    def __init__(self, request, template, context=None, content_type=None, status=None,
                 current_app=_current_app_undefined, charset=None, using=None, snippet_names=None):
        super(SnippetsTemplateResponse, self).__init__(request, template, context, content_type, status,
                                                       current_app, charset, using)
        self.snippet_names = snippet_names

    def render_snippet(self, template, context, snippet_name):
        snippet_template = context.render_context.get('snippets', {}).get(snippet_name)
        return snippet_template.render_content(context) if snippet_template else None

    @property
    def rendered_content(self):
        template = self._resolve_template(self.template_name)
        context = self._resolve_context(self.context_data)

        if not self.snippet_names:
            return template.render(context, self._request)

        context = make_context(context, self._request)
        with context.bind_template(template.template):
            template.template._render(context)
            return self.render_snippet(template, context, self.snippet_names[0])

        return template.render(context, self._request)


class JsonSnippetsTemplateResponse(SnippetsTemplateResponse):

    def __init__(self, request, template, context=None, content_type=None, status=None,
                 current_app=_current_app_undefined, charset=None, using=None, snippet_names=None,
                 extra_snippets=None, extra_content=None, force_snippets=False):

        extra_snippets = extra_snippets or {}
        extra_content = extra_content or {}
        content_type = content_type or (snippet_names or force_snippets) and 'text/plain' or None
        super(JsonSnippetsTemplateResponse, self).__init__(request, template, context, content_type, status,
                                                           current_app, charset, using, snippet_names)
        self.extra_snippets = extra_snippets
        self.extra_content = extra_content
        self.force_snippets = force_snippets
        self['Cache-Control'] = 'no-cache'

    @property
    def rendered_content(self):
        template = self._resolve_template(self.template_name)
        context = self._resolve_context(self.context_data)

        if not self.snippet_names and not self.force_snippets:
            content = template.render(context, self._request)
            return content

        context = make_context(context, self._request)
        with context.bind_template(template.template):
            template.template._render(context)
            snippets = {}

            for snippet_name in self.snippet_names:
                snippets[snippet_name] = self.render_snippet(template, context, snippet_name) or ''

        snippets.update(self.extra_snippets)

        for key, val in snippets.items():
            snippets[key] = clean_html(val)

        output = {
            'snippets': snippets,
        }

        output.update(self.extra_content)
        content = json.dumps(output)
        return content
