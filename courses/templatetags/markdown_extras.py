"""
Template tags для рендеринга Markdown с подсветкой синтаксиса
"""
from django import template
from django.utils.safestring import mark_safe
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension

register = template.Library()


@register.filter(name='markdown')
def markdown_format(text):
    """
    Конвертирует Markdown в HTML с подсветкой синтаксиса кода
    
    Использование в шаблоне:
        {% load markdown_extras %}
        {{ lesson.content|markdown }}
    """
    if not text:
        return ''
    
    # Настройка расширений
    extensions = [
        'markdown.extensions.fenced_code',  # ```code```
        'markdown.extensions.tables',        # Таблицы
        'markdown.extensions.toc',           # Содержание
        'markdown.extensions.nl2br',         # Переносы строк
        'markdown.extensions.extra',         # Дополнительные возможности (включает HTML)
        CodeHiliteExtension(
            css_class='codehilite',
            linenums=False,
            guess_lang=True,
        ),
    ]
    
    md = markdown.Markdown(extensions=extensions)
    html = md.convert(text)
    
    return mark_safe(html)


@register.filter(name='markdown_safe')
def markdown_safe(text):
    """
    Безопасный Markdown (без HTML тегов в исходнике)
    """
    if not text:
        return ''
    
    import bleach
    
    # Сначала конвертируем markdown
    html = markdown_format(text)
    
    # Затем очищаем опасные теги
    allowed_tags = [
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'strong', 'em', 'code', 'pre', 'blockquote',
        'ul', 'ol', 'li', 'a', 'img', 'br', 'hr',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'div', 'span',
    ]
    allowed_attrs = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'code': ['class'],
        'pre': ['class'],
        'div': ['class'],
        'span': ['class'],
    }
    
    return mark_safe(bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs))
