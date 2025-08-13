from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(needs_autoescape=True)
def highlight(text: str, q: str, autoescape: bool = True) -> str:
    """
    Подсвечивает <mark> все целые слова из q (без регистра).
    Безопасно: исходный текст экранируется при autoescape=True.
    """
    if not text or not q:
        return text

    s = str(text)
    if autoescape:
        s = escape(s)

    # слова длиной > 1 (латиница/кириллица/цифры/дефис/подчёркивание)
    tokens = [t for t in re.findall(r"[\w-]+", q, flags=re.UNICODE) if len(t) > 1]
    if not tokens:
        return s

    # \b — границы слов, чтобы не подсвечивать “art” в “part”
    parts = [rf"\b{re.escape(t)}\b" for t in tokens]
    pattern = re.compile(r"(" + "|".join(parts) + r")", re.IGNORECASE | re.UNICODE)

    return mark_safe(pattern.sub(r"<mark>\1</mark>", s))
