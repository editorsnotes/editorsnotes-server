# -*- coding: utf-8 -*-

from pyelasticsearch import ElasticHttpError

from ..api.tests import ClearContentTypesTransactionTestCase
from . import get_index

class SearchTestCase(ClearContentTypesTransactionTestCase):
    def setUp(self):
        en_index = get_index('main')
        if en_index.exists():
            en_index.delete()
        en_index.create()
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
