# -*- coding: utf-8 -*-

import unittest
import pymarc

try:
    import json
except ImportError:
    import simplejson as json

class JsonReaderTest(unittest.TestCase):
    def setUp(self):
        self.reader = pymarc.JSONReader(open('test/test.json'))
        self.in_json = json.load(open('test/test.json'),strict=False)

    def testRoundtrip(self):
        """Tests that result of loading records from the test file
        produces objects deeply equal to the result of loading
        marc-in-json files directly"""
        recs = list(self.reader)
        self.assertEquals(len(self.in_json), len(recs),"Incorrect number of records found")
        for i,rec in enumerate(recs):
            deserialized = json.loads(rec.as_json(),strict=False)
            comp = self.in_json[i]
            self.assertEqual(comp,deserialized)

class JsonTest(unittest.TestCase):

    def setUp(self):
        self.reader = pymarc.MARCReader(open('test/test.dat'))
        self._record = pymarc.Record()
        field = pymarc.Field(
            tag='245',
            indicators=['1', '0'],
            subfields=['a', 'Python', 'c', 'Guido'])
        self._record.add_field(field)

    def test_as_dict_single(self):
        _expected = {
            'fields': [
                {
                    '245':  {
                        'ind1': '1',
                        'ind2': '0',
                        'subfields': [
                            {'a': 'Python'},
                            {'c': 'Guido'}
                        ]
                    }
                }
            ],
            'leader': '          22        4500'
        }
        self.assertEqual(_expected, self._record.as_dict())

    def test_as_json_types(self):
        rd = self._record.as_dict()
        self.assertTrue(isinstance(rd, dict))
        self.assertTrue(isinstance(rd['leader'], str))
        self.assertTrue(isinstance(rd['fields'], list))
        self.assertTrue(isinstance(rd['fields'][0], dict))
        self.assertTrue(isinstance(rd['fields'][0], dict))
        self.assertTrue(isinstance(rd['fields'][0]['245']['ind1'], str))
        self.assertTrue(isinstance(rd['fields'][0]['245']['ind2'], str))
        self.assertTrue(isinstance(rd['fields'][0]['245']['subfields'], list))
        self.assertTrue(
            isinstance(rd['fields'][0]['245']['subfields'][0], dict))
        self.assertTrue(
            isinstance(rd['fields'][0]['245']['subfields'][0]['a'], str))
        self.assertTrue(
            isinstance(rd['fields'][0]['245']['subfields'][1]['c'], str))

    def test_as_json_simple(self):
        record = json.loads(self._record.as_json())

        self.assertTrue('leader' in record)
        self.assertEquals(record['leader'], '          22        4500')

        self.assertTrue('fields' in record)
        self.assertTrue('245' in record['fields'][0])
        self.assertEquals(record['fields'][0]['245'], {
            'subfields': [
                {'a': 'Python'},
                {'c': 'Guido'}
            ],
            'ind2': '0',
            'ind1': '1'})

    def test_as_json_multiple(self):
        for record in self.reader:
            self.assertTrue(str in record.as_json().__class__.__bases__)
            self.assertEquals(dict, json.loads(record.as_json()).__class__)


def suite():
    test_suite = unittest.makeSuite(JsonTest, 'test')
    return test_suite

if __name__ == '__main__':
    unittest.main()
