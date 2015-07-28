from django.template import Template

from rest_framework import renderers

import json

class HTMLRedirectRenderer(renderers.TemplateHTMLRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context['response']
        if response.exception:
            return super(HTMLRedirectRenderer, self).render(data,
                                                            accepted_media_type,
                                                            renderer_context)
        else:
            return '<h1>415: Unsupported Media Type</h1>'

class BrowsableJSONAPIRenderer(renderers.BrowsableAPIRenderer):
    def get_default_renderer(self, view):
        return renderers.JSONRenderer()
