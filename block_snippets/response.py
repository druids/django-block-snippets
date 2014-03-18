import json

from django.template.response import TemplateResponse
from django.template.loader_tags import BlockNode, ExtendsNode

from block_snippets.templatetags import SnippetsIncludeNode
from block_snippets.utils import clean_html
from block_snippets.templatetags.snippets import SnippetNode


class SnippetNotFound(Exception):
    pass


class SnippetsTemplateResponse(TemplateResponse):

    def __init__(self, request, template, context=None, content_type=None,
            status=None, mimetype=None, current_app=None, snippet_names=None):
        super(SnippetsTemplateResponse, self).__init__(request, template, context, content_type, status, mimetype,
                                                       current_app)
        self.snippet_names = snippet_names

    def _get_node(self, nodelist, context, snippet_name):
        for node in nodelist:
            if isinstance(node, SnippetNode) and node.get_name(context) == snippet_name:
                return node
            for key in ('nodelist', 'nodelist_true', 'nodelist_false'):
                if hasattr(node, key):
                    try:
                        return self._get_node(getattr(node, key), context, snippet_name)
                    except:
                        pass
            if isinstance(node, SnippetsIncludeNode):
                t = node.get_nodelist(context)
                t._render(context)
                subnode = self._get_node(t, context, snippet_name)
                if subnode:
                    return subnode

        for node in nodelist:
            if isinstance(node, ExtendsNode):
                subnode = self._get_node(node.get_parent(context), context, snippet_name)
                if subnode:
                    return subnode

        raise SnippetNotFound

    def render_snippet(self, template, context, snippet_name):
        try:
            template._render(context)
            snippet_template = self._get_node(template, context, snippet_name)
            template = snippet_template
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
        content_type = content_type or (snippet_names or force_snippets) and 'application/json' or None
        super(JsonSnippetsTemplateResponse, self).__init__(request, template, context, content_type, status, mimetype,
                                                           current_app, snippet_names)
        self.extra_snippets = extra_snippets
        self.extra_content = extra_content
        self.force_snippets = force_snippets

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
