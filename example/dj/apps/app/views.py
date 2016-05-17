from __future__ import unicode_literals

from block_snippets.views import SnippetTemplateResponseMixin, JSONSnippetTemplateResponseMixin

from django.views.generic import TemplateView


class SnippetsTemplateView(SnippetTemplateResponseMixin, TemplateView):
    template_name = 'snippet.html'


class JSONSnippetsTemplateView(JSONSnippetTemplateResponseMixin, TemplateView):
    template_name = 'snippet.html'
