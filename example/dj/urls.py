from distutils.version import StrictVersion

import django
from django.conf.urls import url

from app.views import SnippetsTemplateView, JSONSnippetsTemplateView


urlpatterns = [
    url(r'^snippet/', SnippetsTemplateView.as_view()),
    url(r'^json-snippet/', JSONSnippetsTemplateView.as_view()),
]

if StrictVersion(django.get_version()) < StrictVersion('1.9'):
    from django.conf.urls import patterns

    urlpatterns = patterns('', *urlpatterns)
