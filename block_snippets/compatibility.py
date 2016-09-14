import django
from django.template.response import TemplateResponse

from distutils.version import StrictVersion


class CompatibleTemplateResponse(TemplateResponse):

    def compatible_render_context(self, snippet_template, context):
        if StrictVersion(django.get_version()) >= StrictVersion('1.8'):
            return snippet_template._rendered_context if snippet_template is not None else ''
        else:
            return snippet_template.render_content(context) if snippet_template is not None else ''

    def compatible_resolve_template(self):
        if (StrictVersion(django.get_version()) < StrictVersion('1.8') or
                StrictVersion(django.get_version()) >= StrictVersion('1.10')):
            return self.resolve_template(self.template_name)
        else:
            return self._resolve_template(self.template_name)

    def compatible_resolve_context(self):
        if (StrictVersion(django.get_version()) < StrictVersion('1.8') or
                StrictVersion(django.get_version()) >= StrictVersion('1.10')):
            return self.resolve_context(self.context_data)
        else:
            return self._resolve_context(self.context_data)

    def compatible_render_template(self, template, context):
        if StrictVersion(django.get_version()) >= StrictVersion('1.8'):
            return template.render(context, self._request)
        else:
            return template.render(context)

    def compatible_call_render(self, func, template, context, *args, **kwargs):
        if StrictVersion(django.get_version()) >= StrictVersion('1.8'):
            from django.template.context import make_context

            context = make_context(context, self._request)
            with context.bind_template(template.template):
                template.template._render(context)
                return func(template, context, *args, **kwargs)
        else:
            template._render(context)
            return func(template, context, *args, **kwargs)