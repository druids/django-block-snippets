from __future__ import unicode_literals

from django.template.base import Node, TemplateSyntaxError
from django import template
from django.forms.util import flatatt

register = template.Library()


class SnippetNode(Node):

    def __init__(self, name, method, web_link, nodelist):
        self.nodelist = nodelist
        self.name = name
        self.method = method
        self.web_link = web_link

    def get_name(self, context):
        return self.name.resolve(context)

    def render(self, context):
        snippets = context.render_context['snippets'] = context.render_context.get('snippets', {})
        snippets[self.get_name(context)] = self
        class_name = 'snippet snippet-' + self.get_name(context).split('-')[-1]
        attrs = {'data-snippet': self.get_name(context), 'data-snippet-type': self.method.resolve(context),
                 'class': class_name}
        if self.web_link:
            attrs['data-web-link'] = self.web_link.resolve(context)
        return '<div%s>%s</div>' % (flatatt(attrs), self.nodelist.render(context))

    def __repr__(self):
        return '<SnippetNode>'


@register.tag('snippet')
def do_snippet(parser, token):
    bits = token.contents.split()
    if len(bits) != 3 and len(bits) != 4:
        raise TemplateSyntaxError("'%s' tag takes two or three arguments" % bits[0])
    snippet_name = parser.compile_filter(bits[1])
    snippet_method = parser.compile_filter(bits[2])
    snippet_web_link = None
    if len(bits) == 4:
        snippet_web_link = parser.compile_filter(bits[3])

    nodelist = parser.parse(('endsnippet',))
    parser.delete_first_token()
    return SnippetNode(snippet_name, snippet_method, snippet_web_link, nodelist)
