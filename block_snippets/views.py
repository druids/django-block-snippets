from block_snippets.response import SnippetsTemplateResponse, JsonSnippetsTemplateResponse


class SnippetTemplateResponseMixin(object):
    response_class = SnippetsTemplateResponse
    allowed_snippets = ()
    allow_all_snippets = False

    def get_snippet_names(self):
        snippets = []

        for snippet in self.request.GET.getlist('snippet'):
            if self.allow_all_snippets or snippet in self.allowed_snippets:
                snippets.append(snippet)

        return snippets

    def render_to_response(self, context, **response_kwargs):
        return super(SnippetTemplateResponseMixin, self).render_to_response(context, block_names=self.get_snippet_names(),
                                                                            **response_kwargs)


class JsonSnippetTemplateResponseMixin(SnippetTemplateResponseMixin):
    response_class = JsonSnippetsTemplateResponse
