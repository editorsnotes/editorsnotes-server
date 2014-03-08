from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.tag(name='deployment_info')
def do_deployment_info(parser, token):
    return DeploymentInfoNode()

class DeploymentInfoNode(template.Node):
    def __init__(self):
        self.empty_context = template.Context({})
    def get_template_or_none(self, template_name):
        try:
            _template = template.loader\
                    .get_template(template_name)\
                    .render(self.empty_context)\
                    .strip()
        except template.TemplateDoesNotExist:
            _template = None
        return _template
    def render(self, context):
        version = self.get_template_or_none('version.txt')
        time_deployed = self.get_template_or_none('time-deployed.txt')

        if not (version and time_deployed):
            return ''

        version_url = self.get_template_or_none('version-url.txt')

        version_repr = '<a href="{}">{}</a>'.format(version_url, version) \
                if version_url else version

        return mark_safe('Version {}, deployed {}.'.format(version_repr, time_deployed))
