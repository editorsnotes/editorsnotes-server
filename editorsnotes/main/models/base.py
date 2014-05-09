# -*- coding: utf-8 -*-

import itertools
import numbers

from django.conf import settings
from django.core import urlresolvers
from django.db import connection, models
from django.utils.html import conditional_escape

from .. import utils

class CreationMetadata(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, related_name='created_%(class)s_set')
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        abstract = True
        get_latest_by = 'created'

class LastUpdateMetadata(CreationMetadata):
    last_updater = models.ForeignKey(settings.AUTH_USER_MODEL, editable=False, related_name='last_to_update_%(class)s_set')
    last_updated = models.DateTimeField(auto_now=True)    
    class Meta:
        abstract = True

class Administered():
    def get_admin_url(self):
        return urlresolvers.reverse(
            'admin:main_%s_change' % self._meta.module_name,
            args=(self.get_affiliation().slug, self.id,))

class URLAccessible():
    @models.permalink
    def get_absolute_url(self):
        return ('%s_view' % self._meta.module_name, [str(self.id)])
    def __unicode__(self):
        return utils.truncate(self.as_text())
    def as_text(self):
        raise Exception('Must implement %s.as_text()' % self._meta.module_name)
    def as_html(self):
        return '<span class="%s">%s</span>' % (
            self._meta.module_name, conditional_escape(self.as_text()))

class OrderingManager(models.Manager):
    """
    A manager which can explicitly set the ordering of its querysets.
    """
    use_for_related_fields = True
    @staticmethod
    def normalize_position_dict(positions_dict):
        """
        Given a dict, will return a new dict with the same keys, and int values
        incrementing from 1.
        """
        items = sorted(positions_dict.items(), key=lambda x: x[1])
        counter = itertools.count(1)
        return dict(zip([item for item, order in items], counter))
    def _generate_update_sql(self, ordering_field, positions_dict):
        """
        Returns SQL and params necessary to update given field and positions.
        """
        statement = (
            """
            UPDATE {table_name} SET {ordering_field} = positions.ordering
            FROM (
                SELECT unnest(%s) as id, unnest(%s) as ordering
            ) AS positions 
            WHERE {table_name}.id = positions.id;
            """
        ).format(table_name=self.model._meta.db_table,
                 ordering_field=ordering_field)
        return statement, map(list, zip(*positions_dict.items()))
    def _ensure_integer_field(self, ordering_field_name):
        if ordering_field_name not in self.model._meta.get_all_field_names():
            raise ValueError('{} is not a field of {}.'.format(ordering_field_name, self.model))
        ordering_field = self.model._meta.get_field_by_name(ordering_field_name)
        if not isinstance(ordering_field[0], models.IntegerField):
            raise ValueError('{} can only manage integer ordering fields; '
                             '{} is an instance of {}.'.format(
                                 self, ordering_field_name, ordering_field.__class__))
    def bulk_update_order(self, ordering_field, positions, fill_in_empty=False):
        """
        Bulk update an ordering field for a queryset.

        Arguments:
        ordering_field - The field on the model which should be treated as
            the ordering field. Must be an instence of IntegerField.
        positions - A dict or dict-like object in the format of (id, position).
        fill_in_empty - Behavior of the method depends on this flag only if
            there are IDs from the queryset that are not present in `positions`.
            If set to False, it will raise a ValueError. If set to True, it will
            append the omitted item IDs to the end of the ordering with whatever
            the default order of the queryset is.
        """
        self._ensure_integer_field(ordering_field)
        positions_dict = dict(positions)
        if not all((isinstance(p, numbers.Number) for p in positions.values())):
            raise ValueError('All position values must be numbers.')
        positions_dict = OrderingManager.normalize_position_dict(positions_dict)
        collection_ids = self.get_query_set().values_list('id', flat=True)
        missing_ids = set(collection_ids) - set(positions_dict.keys()) 
        if len(missing_ids):
            if not fill_in_empty:
                raise ValueError('Ordering not provided for every member of collection.')
            else:
                # Keep default ordering, whatever it is, and increment.
                counter = itertools.count(max(positions_dict.values()) + 1)
                positions_dict.update(dict(zip(missing_ids, counter)))
        query, params = self._generate_update_sql(ordering_field, positions_dict)
        cursor = connection.cursor()
        cursor.execute(query, params)
