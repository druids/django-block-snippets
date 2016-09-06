from __future__ import unicode_literals

import json

from block_snippets.utils import clean_html

from .compatibility import CompatibleTemplateResponse


class SnippetsTemplateResponse(CompatibleTemplateResponse):

    def __init__(self, *args, **kwargs):
        self.snippet_names = kwargs.pop('snippet_names', None)
        super(SnippetsTemplateResponse, self).__init__(*args, **kwargs)

    def render_snippet(self, template, context, snippet_name):
        return self.compatible_render_context(context.render_context.get('snippets', {}).get(snippet_name), context)

    @property
    def rendered_content(self):
        template = self.compatible_resolve_template()
        context = self.compatible_resolve_context()
        if not self.snippet_names:
            return self.compatible_render_template(template, context)
        else:
            return self.compatible_call_render(self.render_snippet, template, context, self.snippet_names[0])

class JSONSnippetsTemplateResponse(SnippetsTemplateResponse):

    def __init__(self, *args, **kwargs):
        extra_snippets = kwargs.pop('extra_snippets', {})
        extra_content = kwargs.pop('extra_content', {})
        content_type = kwargs.pop('content_type', None)
        snippet_names = kwargs.get('snippet_names', None)
        force_snippets = kwargs.pop('force_snippets', None)
        kwargs['content_type'] = (
            content_type if content_type is not None or (not snippet_names and not force_snippets) else 'text/plain'
        )
        super(JSONSnippetsTemplateResponse, self).__init__(*args, **kwargs)
        self.extra_snippets = extra_snippets
        self.extra_content = extra_content
        self.force_snippets = force_snippets
        self['Cache-Control'] = 'no-cache'

    def render_snippets(self, template, context):
        return {snippet_name: self.render_snippet(template, context, snippet_name) or ''
                for snippet_name in self.snippet_names}

    @property
    def rendered_content(self):
        template = self.compatible_resolve_template()
        context = self.compatible_resolve_context()
        if not self.snippet_names and not self.force_snippets:
            return self.compatible_render_template(template, context)
        else:
            snippets = self.compatible_call_render(self.render_snippets, template, context)
            snippets.update(self.extra_snippets)
            snippets = {key: clean_html(val) for key, val in snippets.items()}
            output = {'snippets': snippets}
            output.update(self.extra_content)
            return json.dumps(output)
