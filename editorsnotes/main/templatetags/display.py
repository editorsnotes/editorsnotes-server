from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from editorsnotes.main import utils
from editorsnotes.main.models import UserProfile
from isodate import datetime_isoformat
from lxml import etree

register = template.Library()

@register.filter
def as_text(tree):
    return utils.xhtml_to_text(tree)

@register.filter
def as_html(tree):
    return mark_safe(etree.tostring(tree))

@register.filter
def as_link(obj):
    return mark_safe(
        '<a class="model-link %s-link" href="%s">%s</a>' % (
            obj._meta.module_name, obj.get_absolute_url(), obj.as_html()))

@register.filter
def timeago(datetime):
    return mark_safe(
        '<time class="timeago" datetime="%s">%s</time>' % (
            datetime_isoformat(datetime), datetime.strftime('%I:%M%p, %b %d %Y')))

@register.filter
def display_last_updated(obj):
    if 'last_updated' in obj._meta.get_all_field_names():
        return mark_safe(
            '''<div class="last-updated">Last edited by %s %s.</div>''' % (
                as_link(UserProfile.get_for(obj.last_updater)), timeago(obj.last_updated)))
    else:
        return mark_safe(
            '''<div class="last-updated">Last edited by %s %s.</div>''' % (
                as_link(UserProfile.get_for(obj.creator)), timeago(obj.created)))

@register.filter
def display_edit_history(obj):
    return mark_safe(
        '''<div class="edit-history">
Created by %s %s.<br/>
Last edited by %s %s.</div>''' % (
            as_link(UserProfile.get_for(obj.creator)), timeago(obj.created),
            as_link(UserProfile.get_for(obj.last_updater)), timeago(obj.last_updated)))
