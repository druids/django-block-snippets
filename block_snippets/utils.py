from __future__ import unicode_literals

from django.utils.html import strip_spaces_between_tags


def clean_html(html):
    return strip_spaces_between_tags(html)
