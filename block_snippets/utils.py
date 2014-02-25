import re


def clean_html(html):
    return re.sub(r'[\t\n\r]', '', html)
