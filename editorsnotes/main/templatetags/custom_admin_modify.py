from django import template
from django.contrib.admin.templatetags.admin_modify import submit_row

register = template.Library()

def custom_submit_row(context):
    o = submit_row(context)
    o['request'] = context['request']
    return o
custom_submit_row = register.inclusion_tag('admin/submit_line.html', takes_context=True)(custom_submit_row)
