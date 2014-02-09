from django.template.response import TemplateResponse
from django.template.loader_tags import BlockNode, ExtendsNode

from block_snippets.templatetags import SnippetsIncludeNode


class BlockNotFound(Exception):
    pass


class SnippetsTemplateResponse(TemplateResponse):

    def __init__(self, request, template, context=None, content_type=None,
            status=None, mimetype=None, current_app=None, block_name=None):
        super(SnippetsTemplateResponse, self).__init__(request, template, context, content_type, status, mimetype,
                                                       current_app)
        self.block_name = block_name


    def _get_node(self, nodelist, context):
        for node in nodelist:
            if isinstance(node, BlockNode) and node.name == self.block_name:
                return node
            for key in ('nodelist', 'nodelist_true', 'nodelist_false'):
                if hasattr(node, key):
                    try:
                        return self._get_node(getattr(node, key), context)
                    except:
                        pass
            if isinstance(node, SnippetsIncludeNode):
                t = node.get_nodelist(context)
                t._render(context)
                subnode = self._get_node(t, context)
                if subnode:
                    return subnode

        for node in nodelist:
            if isinstance(node, ExtendsNode):
                subnode = self._get_node(node.get_parent(context), context)
                if subnode:
                    return subnode

        raise BlockNotFound

    @property
    def rendered_content(self):
        template = self.resolve_template(self.template_name)
        context = self.resolve_context(self.context_data)

        block_template = template

        try:
            if self.block_name:
                template._render(context)
                block_template = self._get_node(template, context)
                template = block_template
        except BlockNotFound:
            pass

        content = block_template.render(context)
        return content
