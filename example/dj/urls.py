import django
from django.conf.urls import patterns, url

from app.views import SnippetsTemplateView, JSONSnippetsTemplateView


urlpatterns = [
    url(r'^snippet/', SnippetsTemplateView.as_view()),
    url(r'^json-snippet/', JSONSnippetsTemplateView.as_view()),
]

if django.get_version() < '1.9':
    urlpatterns = patterns('', *urlpatterns)
