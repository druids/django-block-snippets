import json

from block_snippets.utils import clean_html

from django.template.response import TemplateResponse


class SnippetsTemplateResponse(TemplateResponse):

    def __init__(self, *args, **kwargs):
        self.snippet_names = kwargs.pop('snippet_names', None)
        super(SnippetsTemplateResponse, self).__init__(*args, **kwargs)

    def render_snippet(self, context, snippet_name):
        snippet_template = context.render_context.get('snippets', {}).get(snippet_name)
        return snippet_template._rendered_context if snippet_template is not None else ''

    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)
        if not self.snippet_names:
            return template.render(context, self._request)
        else:
            return self.call_render(self.render_snippet, template, context, self.snippet_names[0])

    def call_render(self, func, template, context, *args, **kwargs):
        from django.template.context import make_context

        context = make_context(context, self._request)
        with context.bind_template(template.template):
            template.template._render(context)
            return func(context, *args, **kwargs)


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

    def render_snippets(self, context):
        return {snippet_name: self.render_snippet(context, snippet_name) or ''
                for snippet_name in self.snippet_names}

    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)
        if not self.snippet_names and not self.force_snippets:
            return template.render(context, self._request)
        else:
            snippets = self.call_render(self.render_snippets, template, context)
            snippets.update(self.extra_snippets)
            snippets = {key: clean_html(val) for key, val in snippets.items()}
            output = {'snippets': snippets}
            output.update(self.extra_content)
            return json.dumps(output)
