# -*- coding: utf-8 -*-

from django.test import TransactionTestCase

from pyelasticsearch import ElasticHttpError

from ..api.tests import ClearContentTypesMixin
from .items.helpers import perform_query

class SearchTestCase(ClearContentTypesMixin, TransactionTestCase):
    def test_escape_special_chars(self):
        "Queries with special characters shouldn't raise an error from ES"
        es_special_chars = list('+\-&|!(){}[]^~*?:/\\"')
        es_special_chars += ['""', '{}', '"phrase""']

        for query in es_special_chars:
            try:
                perform_query(query)
            except ElasticHttpError:
                self.fail('Search for query “{}” raised an exception.'.format(query))
