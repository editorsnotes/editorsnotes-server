# -*- coding: utf-8 -*-

from django.test import TransactionTestCase

from pyelasticsearch import ElasticHttpError

from ..api.tests import ClearContentTypesMixin
from . import get_index

class SearchTestCase(ClearContentTypesMixin, TransactionTestCase):
    def test_escape_special_chars(self):
        "Queries with special characters shouldn't raise an error from ES"
        es_special_chars = list('+\-&|!(){}[]^~*?:/\\"')
        es_special_chars += ['""', '{}', '"phrase""']

        en_index = get_index('main')
        for query in es_special_chars:
            try:
                en_index.search(query)
            except ElasticHttpError:
                self.fail('Search for query “{}” raised an exception.'.format(query))
