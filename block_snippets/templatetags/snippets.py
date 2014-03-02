from django.template.base import Node, TemplateSyntaxError
from django import template

register = template.Library()


class SnippetNode(Node):

    def __init__(self, name, method, nodelist):
        self.nodelist = nodelist
        self.name = name
        self.method = method

    def get_name(self, context):
        return self.name.resolve(context)

    def render(self, context):
        name = self.get_name(context)
        method = self.method.resolve(context)
        output = self.nodelist.render(context)
        return '<div data-snippet="%s" data-snippet-type="%s">%s</div>' % (name, method, output)


@register.tag('snippet')
def do_snippet(parser, token):
    bits = token.contents.split()
    if len(bits) != 3:
        raise TemplateSyntaxError("'%s' tag takes two arguments" % bits[0])
    snippet_name = bits[1]
    snippet_method = bits[2]

    try:
        if snippet_name in parser.__loaded_snippets:
            raise TemplateSyntaxError("'%s' tag with name '%s' appears more than once" % (bits[0], snippet_name))
        parser.__loaded_snippets.append(snippet_name)
    except AttributeError:  # parser.__loaded_blocks isn't a list yet
        parser.__loaded_snippets = [snippet_name]
    nodelist = parser.parse(('endsnippet',))
    parser.delete_first_token()
    return SnippetNode(parser.compile_filter(snippet_name), parser.compile_filter(snippet_method), nodelist)
