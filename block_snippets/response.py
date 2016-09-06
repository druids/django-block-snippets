from __future__ import unicode_literals

import json

from distutils.version import StrictVersion

import django
from django.template.response import TemplateResponse

from block_snippets.utils import clean_html


class SnippetsTemplateResponse(TemplateResponse):

    def __init__(self, *args, **kwargs):
        self.snippet_names = kwargs.pop('snippet_names', None)
        super(SnippetsTemplateResponse, self).__init__(*args, **kwargs)

    def render_snippet(self, template, context, snippet_name):
        snippet_template = context.render_context.get('snippets', {}).get(snippet_name)
        if StrictVersion(django.get_version()) >= StrictVersion('1.8'):
            return snippet_template._rendered_context if snippet_template is not None else ''
        else:
            return snippet_template.render_content(context) if snippet_template is not None else ''

    @property
    def rendered_content(self):
        if (StrictVersion(django.get_version()) < StrictVersion('1.8') or
                StrictVersion(django.get_version()) >= StrictVersion('1.10')):
            template = self.resolve_template(self.template_name)
            context = self.resolve_context(self.context_data)
        else:
            template = self._resolve_template(self.template_name)
            context = self._resolve_context(self.context_data)

        if StrictVersion(django.get_version()) >= StrictVersion('1.8'):
            from django.template.context import make_context

            if not self.snippet_names:
                return template.render(context, self._request)

            context = make_context(context, self._request)
            with context.bind_template(template.template):
                template.template._render(context)
                return self.render_snippet(template, context, self.snippet_names[0])

            return template.render(context, self._request)
        else:
            if not self.snippet_names:
                return template.render(context)

            template._render(context)
            return self.render_snippet(template, context, self.snippet_names[0])


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

    @property
    def rendered_content(self):
        if (StrictVersion(django.get_version()) < StrictVersion('1.8') or
                    StrictVersion(django.get_version()) >= StrictVersion('1.10')):
            template = self.resolve_template(self.template_name)
            context = self.resolve_context(self.context_data)

        else:
            template = self._resolve_template(self.template_name)
            context = self._resolve_context(self.context_data)

        if StrictVersion(django.get_version()) >= StrictVersion('1.8'):
            from django.template.context import make_context

            if not self.snippet_names and not self.force_snippets:
                return template.render(context, self._request)
            context = make_context(context, self._request)
            with context.bind_template(template.template):
                template.template._render(context)
                snippets = {}
                for snippet_name in self.snippet_names:
                    snippets[snippet_name] = self.render_snippet(template, context, snippet_name) or ''

        else:
            if not self.snippet_names and not self.force_snippets:
                return template.render(context)
            template._render(context)
            snippets = {}
            for snippet_name in self.snippet_names:
                snippets[snippet_name] = self.render_snippet(template, context, snippet_name) or ''

        snippets.update(self.extra_snippets)
        for key, val in snippets.items():
            snippets[key] = clean_html(val)
        output = {'snippets': snippets}
        output.update(self.extra_content)
        return json.dumps(output)
