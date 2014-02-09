from block_snippets.response import SnippetsTemplateResponse


class SnippetTemplateResponseMixin(object):
    response_class = SnippetsTemplateResponse
    allowed_snippets = ()

    def get_snippet_name(self):
        snippet = self.request.GET.get('snippet')
        if snippet and snippet not in self.allowed_snippets:
            snippet = None
        return snippet

    def render_to_response(self, context, **response_kwargs):
        return super(SnippetTemplateResponseMixin, self).render_to_response(context, block_name=self.get_snippet_name(),
                                                                            **response_kwargs)