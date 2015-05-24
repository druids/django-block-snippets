from __future__ import unicode_literals

from django.template.base import Node, TemplateSyntaxError
from django import template
from django.forms.utils import flatatt

register = template.Library()


class SnippetNode(Node):

    def __init__(self, name, method, web_link, nodelist):
        self.nodelist = nodelist
        self.name = name
        self.method = method
        self.web_link = web_link

    def get_name(self, context):
        return self.name.resolve(context)

    def render_content(self, context):
        return self.nodelist.render(context)

    def render(self, context):
        snippets = context.render_context['snippets'] = context.render_context.get('snippets', {})
        snippets[self.get_name(context)] = self
        class_name = 'snippet snippet-' + self.get_name(context).split('-')[-1]
        attrs = {'data-snippet': self.get_name(context), 'data-snippet-type': self.method.resolve(context),
                 'class': class_name}
        if self.web_link:
            attrs['data-web-link'] = self.web_link.resolve(context)
        return '<div%s>%s</div>' % (flatatt(attrs), self.render_content(context))

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


class SnippetLoaderNode(Node):

    def __init__(self, nodelist, loader, type, web_link=None, onload=None):
        self.nodelist = nodelist
        self.loader = loader
        self.type = type
        self.web_link = web_link
        self.onload = onload

    def render_content(self, context):
        return self.nodelist.render(context)

    def render(self, context):
        attrs = {
                 'data-snippet-loader': self.loader.resolve(context),
                 'data-snippet-type': self.type.resolve(context),
                 }
        if self.web_link:
            attrs['data-web-link'] = self.web_link.resolve(context)
        if self.onload:
            attrs['data-snippet-onload'] = self.onload.resolve(context)
        if self.web_link:
            attrs['data-web-link'] = self.web_link.resolve(context)
        return '<div class="snippet snippet-content"%s>%s</div>' % (flatatt(attrs), self.render_content(context))

@register.tag('snippet_loader')
def do_snippet_loader(parser, token):
    tag_args = []
    tag_kwargs = {'type': parser.compile_filter('"replace"')}

    for content in token.split_contents()[1:]:
        if '=' in content:
            tag_kwargs[content.split('=', 1)[0]] = parser.compile_filter(content.split('=', 1)[1])
        else:
            tag_args.append(parser.compile_filter(content))

    if not tag_args:
        raise TemplateSyntaxError("'snippet_loader' tag must have selected some loaders")
    nodelist = parser.parse(('endsnippet_loader',))
    parser.delete_first_token()
    return SnippetLoaderNode(nodelist, *tag_args, **tag_kwargs)
