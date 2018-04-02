from block_snippets.response import SnippetsTemplateResponse, JSONSnippetsTemplateResponse


class SnippetTemplateResponseMixin:
    response_class = SnippetsTemplateResponse
    allow_all_snippets = False

    def get_snippet_names(self):
        return self.request.GET.getlist('snippet')

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['snippet_names'] = response_kwargs.get('snippet_names', self.get_snippet_names())
        return super(SnippetTemplateResponseMixin, self).render_to_response(context, **response_kwargs)

    def has_snippet(self):
        return bool(self.get_snippet_names())


class JSONSnippetTemplateResponseMixin(SnippetTemplateResponseMixin):
    response_class = JSONSnippetsTemplateResponse
