import datetime
import json

from django.db import models
from django.utils.translation import ugettext as _

from . import utils
from .fields import ZoteroField

class ZoteroLink(models.Model):
    zotero_url = models.URLField(blank=True)
    date_information = models.TextField(blank=True)
    modified = models.DateTimeField(editable=False)
    last_synced = models.DateTimeField(blank=True, null=True)

    def save(self, update_modified=True, *args, **kwargs):
        if update_modified:
            self.modified = datetime.datetime.now()
        super(ZoteroLink, self).save(*args, **kwargs)

class ZoteroItem(models.Model):
    zotero_data = ZoteroField(blank=True, null=True)
    zotero_link = models.OneToOneField(
        ZoteroLink, blank=True, null=True, related_name='zotero_item')

    class Meta:
        abstract = True

    def get_zotero_fields(self):
        if self.zotero_data is None:
            return ()
        zotero_data = json.loads(self.zotero_data)
        zotero_data['itemType'] = _(zotero_data['itemType'])
        if self.zotero_link and self.zotero_link.date_information:
            date_parts = json.loads(self.zotero_link.date_information)
            for part in date_parts:
                zotero_data[part] = date_parts[part]
        if zotero_data['creators']:
            names = zotero_data.pop('creators')
            output = zotero_data.items()
            for name in names:
                output.append(
                    (name['creatorType'], utils.get_creator_name(name)))
        else:
            output = zotero_data.items()
        return output


