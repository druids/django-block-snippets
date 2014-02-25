import re
import json

from django.template.response import TemplateResponse
from django.template.loader_tags import BlockNode, ExtendsNode

from block_snippets.templatetags import SnippetsIncludeNode
from block_snippets.utils import clean_html


class BlockNotFound(Exception):
    pass


class SnippetsTemplateResponse(TemplateResponse):

    def __init__(self, request, template, context=None, content_type=None,
            status=None, mimetype=None, current_app=None, block_names=None):
        super(SnippetsTemplateResponse, self).__init__(request, template, context, content_type, status, mimetype,
                                                       current_app)
        self.block_names = block_names

    def _get_node(self, nodelist, context, block_name):
        for node in nodelist:
            if isinstance(node, BlockNode) and node.name == block_name:
                return node
            for key in ('nodelist', 'nodelist_true', 'nodelist_false'):
                if hasattr(node, key):
                    try:
                        return self._get_node(getattr(node, key), context, block_name)
                    except:
                        pass
            if isinstance(node, SnippetsIncludeNode):
                t = node.get_nodelist(context)
                t._render(context)
                subnode = self._get_node(t, context, block_name)
                if subnode:
                    return subnode

        for node in nodelist:
            if isinstance(node, ExtendsNode):
                subnode = self._get_node(node.get_parent(context), context, block_name)
                if subnode:
                    return subnode

        raise BlockNotFound

    def render_block(self, template, context, block_name):
        try:
            template._render(context)
            block_template = self._get_node(template, context, block_name)
            template = block_template
            return block_template.render(context)
        except BlockNotFound:
            return None

    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)

        if not self.block_names:
            return template.render(context)

        template._render(context)
        return self.render_block(template, context, self.block_names[0])


class JsonSnippetsTemplateResponse(SnippetsTemplateResponse):

    def __init__(self, request, template, context=None, content_type=None,
            status=None, mimetype=None, current_app=None, block_names=None,
            extra_snippets={}, extra_content={}, force_snippets=False):
        content_type = content_type or (block_names or force_snippets) and 'application/json' or None
        super(JsonSnippetsTemplateResponse, self).__init__(request, template, context, content_type, status, mimetype,
                                                           current_app, block_names)
        self.extra_snippets = extra_snippets
        self.extra_content = extra_content
        self.force_snippets = force_snippets

    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)

        if not self.block_names and not self.force_snippets:
            return template.render(context)

        template._render(context)

        snippets = {}
        for block_name in self.block_names:
            snippets[block_name] = re.sub(r'[\t\n\r]', '', self.render_block(template, context, block_name))
        snippets.update(self.extra_snippets)

        for key, val in snippets.items():
            snippets[key] = clean_html(val)

        output = {
                    'snippets': snippets,
                 }

        output.update(self.extra_content)

        return json.dumps(output)
