from block_snippets.response import SnippetsTemplateResponse, JsonSnippetsTemplateResponse


class SnippetTemplateResponseMixin(object):
    response_class = SnippetsTemplateResponse
    allow_all_snippets = False

    def get_snippet_names(self):
        return self.request.GET.getlist('snippet')

    def render_to_response(self, context, **response_kwargs):
        return super(SnippetTemplateResponseMixin, self).render_to_response(context, block_names=self.get_snippet_names(),
                                                                            **response_kwargs)


class JsonSnippetTemplateResponseMixin(SnippetTemplateResponseMixin):
    response_class = JsonSnippetsTemplateResponse
