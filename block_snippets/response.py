from __future__ import unicode_literals

import json

from django.template.response import TemplateResponse

from block_snippets.utils import clean_html


class SnippetNotFound(Exception):
    pass


class SnippetsTemplateResponse(TemplateResponse):

    def __init__(self, request, template, context=None, content_type=None,
            status=None, mimetype=None, current_app=None, snippet_names=None):
        super(SnippetsTemplateResponse, self).__init__(request, template, context, content_type, status, mimetype,
                                                       current_app)
        self.snippet_names = snippet_names

    def render_snippet(self, template, context, snippet_name):
        try:
            snippet_template = context.render_context.get('snippets', {}).get(snippet_name)
            return snippet_template.render(context)
        except SnippetNotFound:
            return None

    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)

        if not self.snippet_names:
            return template.render(context)

        template._render(context)
        return self.render_snippet(template, context, self.snippet_names[0])


class JsonSnippetsTemplateResponse(SnippetsTemplateResponse):

    def __init__(self, request, template, context=None, content_type=None,
            status=None, mimetype=None, current_app=None, snippet_names=None,
            extra_snippets={}, extra_content={}, force_snippets=False):
        content_type = content_type or (snippet_names or force_snippets) and 'text/plain' or None
        super(JsonSnippetsTemplateResponse, self).__init__(request, template, context, content_type, status, mimetype,
                                                           current_app, snippet_names)
        self.extra_snippets = extra_snippets
        self.extra_content = extra_content
        self.force_snippets = force_snippets
        self['Cache-Control'] = 'no-cache'

    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)

        if not self.snippet_names and not self.force_snippets:
            return template.render(context)

        template._render(context)

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

        return json.dumps(output)
