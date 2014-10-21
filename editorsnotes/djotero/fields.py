from collections import OrderedDict
import json

from django.core.exceptions import ValidationError
from django.db import models

from . import utils

class ZoteroField(models.TextField):
    def validate(self, value, model_instance):
        super(ZoteroField, self).validate(value, model_instance)
        if value is None:
            return

        try:
            data = json.loads(value)
        except ValueError:
            raise ValidationError('This field must be valid JSON.')

        item_type = data.get('itemType')
        valid_item_types = [i['itemType'] for i in utils.get_item_types()['itemTypes']]

        if not item_type:
            raise ValidationError('Must provide item type.')
        if item_type not in valid_item_types:
            raise ValidationError('{} is not a valid item type.'.format(item_type))

        valid_fields = utils.get_item_template(item_type).keys()
        bad_fields = set(data.keys()) - set(valid_fields)
        if len(bad_fields):
            raise ValidationError('Invalid fields for {}: {}.'.format(
                item_type, ', '.join(bad_fields)))

    def clean(self, value, model_instance):
        cleaned_value = super(ZoteroField, self).clean(value, model_instance)
        if cleaned_value:
            data = json.loads(cleaned_value)
            cleaned_data = OrderedDict()
            item_template = utils.get_item_template(data['itemType'])
            for key, default_val in item_template.items():
                cleaned_data[key] = data.get(key, default_val) or default_val
            cleaned_value = json.dumps(cleaned_data)
        return cleaned_value
