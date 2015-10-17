from collections import OrderedDict

from rest_framework import renderers

from .ld import CONTEXT


class BrowsableJSONAPIRenderer(renderers.BrowsableAPIRenderer):
    def get_default_renderer(self, view):
        return JSONLDRenderer()


class JSONLDRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        json_with_context = OrderedDict()
        json_with_context['@context'] = CONTEXT.copy()

        json_with_context.update(data)

        data = json_with_context

        return super(JSONLDRenderer, self)\
            .render(data, accepted_media_type, renderer_context)
