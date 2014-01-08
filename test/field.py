# -*- coding: utf-8 -*-

import unittest

from pymarc.exceptions import PymarcException
from pymarc.field import ControlField, Field



class ControlFieldTest(unittest.TestCase):


    def test_string(self):
        tag = '008'
        data = '831227m19799999nyu           ||| | ger  '
        f = ControlField(tag, data)
        self.assertEquals(str(f),
                        "={}  {}".format(tag, data.replace(' ', '\\')))


    def test_binary_string(self):
        tag = b'008'
        data = b'831227m19799999nyu           ||| | ger  '
        f = ControlField(tag, data)
        self.assertEquals(
            str(f),
            "={}  {}".format(tag.decode('ascii'),
                             data.decode('ascii').replace(' ', '\\')))


    def test_binary_value(self):
        tag = b'008'
        data = b'831227m19799999nyu           ||| | ger  '
        f = ControlField(tag, data)
        self.assertEquals(f.value(), data)


    def test_value(self):
        tag = '008'
        data = '831227m19799999nyu           ||| | ger  '
        f = ControlField(tag, data)
        self.assertEquals(f.value(), data)


    def test_non_integer_tag(self):
        f = ControlField("SYS", "abracadabra")
        self.assertEquals(f.tag, "SYS")


    def test_binary_non_integer_tag(self):
        f = ControlField(b"SYS", b"abracadabra")
        self.assertEquals(f.tag, b"SYS")


    def test_tag_normalize(self):
        f = ControlField('2', "abracadabra")
        self.assertEqual(f.tag, '002')
        f.tag = '3'
        self.assertEqual(f.tag, '003')
        f.tag = 'S'
        self.assertEqual(f.tag, '00S')


    def test_binary_tag_normalize(self):
        f = ControlField(b'2', b"abracadabra")
        self.assertEqual(f.tag, b'002')
        f.tag = b'3'
        self.assertEqual(f.tag, b'003')
        f.tag = b'S'
        self.assertEqual(f.tag, b'00S')



class FieldIndicatorsTest(unittest.TestCase):


    def empty(self, space=' '):
        for e in [space+space, space.strip(), None, [], ()]:
            yield e
        em = None, space, space.strip()
        for i1 in em:
            for i2 in em:
                yield i1, i2
                yield [i1, i2]


    def integer(self, space, ints):
        em = None, space, space.strip()
        for i1 in em:
            for i2 in em:
                yield i1, i2
                yield [i1, i2]


    def test_empty_indicators(self):
        f = Field('245')
        self.assertEqual(f.indicator1, ' ')
        self.assertEqual(f.indicator2, ' ')
        self.assertEqual(f.indicators, '  ')
        for e in self.empty():
            f = Field('245', e)
            self.assertEqual(f.indicator1, ' ', "Input: {}".format(e))
            self.assertEqual(f.indicator2, ' ', "Input: {}".format(e))
            self.assertEqual(f.indicators, '  ', "Input: {}".format(e))


    def test_binary_empty_indicators(self):
        f = Field(b'245')
        self.assertEqual(f.indicator1, b' ')
        self.assertEqual(f.indicator2, b' ')
        self.assertEqual(f.indicators, b'  ')
        for e in self.empty(b' '):
            f = Field(b'245', e)
            self.assertEqual(f.indicator1, b' ', "Input: {}".format(e))
            self.assertEqual(f.indicator2, b' ', "Input: {}".format(e))
            self.assertEqual(f.indicators, b'  ', "Input: {}".format(e))


    def test_indicators_number(self):
        for tag, indicators in ((b'245', b' '), (b'245', b'1'), (b'245', [2]),
                                ('245', ' '), ('245', '1'), ('245', [2]),
                                ):
            with self.assertRaisesRegexp(PymarcException,
                                        'Field: Bad indicators number:',
                                        msg="tag={} indicators={}".format(tag, indicators)):
                Field(tag, indicators)


    def test_integer_indicators(self):
        f = Field('245', [1, 2])
        self.assertEqual(f.indicator1, '1')
        self.assertEqual(f.indicator2, '2')
        self.assertEqual(f.indicators, '12')




class FieldTest(unittest.TestCase):

    def setUp(self):
        self.field = Field(
            tag = '245',
            indicators = [ '0', '1' ],
            subfields = [
                'a', 'Huckleberry Finn: ',
                'b', 'An American Odyssey'
            ]
        )

        self.subjectfield = Field('650', ' 0',
            [
                ('a', 'Python (Computer program language)'),
                ('v', 'Poetry.')
            ]
        )

    def test_string(self):
        self.assertEquals(str(self.field),
            '=245  01$aHuckleberry Finn: $bAn American Odyssey')

    def test_indicators(self):
        self.assertEqual(self.field.indicator1, '0')
        self.assertEqual(self.field.indicator2, '1')

    def test_subfields_created(self):
        subfields = self.field.subfields
        self.assertEqual(len(subfields), 2)

    def test_subfield_short(self):
        self.assertEqual(self.field['a'], 'Huckleberry Finn: ')
        self.assertEqual(self.field['z'], None)

    def test_subfields(self):
        self.assertEqual(self.field.get_subfields('a'),
            ['Huckleberry Finn: '])
        self.assertEqual(self.subjectfield.get_subfields('a'),
            ['Python (Computer program language)'])

    def test_subfields_multi(self):
        self.assertEqual(self.field.get_subfields('a','b'),
            ['Huckleberry Finn: ', 'An American Odyssey' ])
        self.assertEqual(self.subjectfield.get_subfields('a','v'),
            ['Python (Computer program language)', 'Poetry.' ])

    def test_encode(self):
        self.field.as_marc()

    def test_membership(self):
        self.assertTrue('a' in self.field)
        self.assertFalse('zzz' in self.field)

    def test_iterator(self):
        string = ""
        for subfield in self.field:
            string += subfield[0]
            string += subfield[1]
        self.assertEquals(string, 'aHuckleberry Finn: bAn American Odyssey')

    def test_value(self):
        self.assertEquals(self.field.value(),
            'Huckleberry Finn: An American Odyssey')

    def test_non_integer_tag(self):
        # make sure this doesn't throw an exception
        field = Field(tag='3 0', indicators=['0', '1'], subfields=['a', 'foo'])
        self.assertEquals(field.tag, '3 0')


    def test_add_subfield(self):
        field = Field(tag='245', indicators=['0', '1'], subfields=['a', 'foo'])
        field.add_subfield('a','bar')
        self.assertEquals(field.__str__(), '=245  01$afoo$abar')

    def test_delete_subfield(self):
        field = Field(tag='200', indicators=['0', '1'], subfields=['a','My Title', 'a', 'Kinda Bogus Anyhow'])
        self.assertEquals(field.delete_subfield('z'), None)
        self.assertEquals(field.delete_subfield('a'), 'My Title')
        self.assertEquals(field.delete_subfield('a'), 'Kinda Bogus Anyhow')
        self.assertTrue(len(field.subfields) == 0)

    def test_is_subject_field(self):
        self.assertEqual(self.subjectfield.is_subject_field(), True,
            'If tag starts with 6 then field is a subject field')
        self.assertEqual(self.field.is_subject_field(), False,
            'Field is a subject one only if its tag starts with 6')

    def test_format_field(self):
        self.subjectfield.add_subfield('6', '880-4')
        self.assertEqual(self.subjectfield.format_field(),
            'Python (Computer program language) -- Poetry.',
            'Field 6 should be skipped by format_field')
        self.field.add_subfield('6', '880-1')
        self.assertEqual(self.field.format_field(),
            'Huckleberry Finn:  An American Odyssey',
            'Field 6 should be skipped by format_field')

    def test_tag_normalize(self):
        f = Field(tag='42')
        self.assertEqual(f.tag, '042')

    def test_alphatag(self):
        f = Field(tag='CAT', indicators=['0', '1'], subfields=['a', 'foo'])
        self.assertEqual(f.tag, 'CAT')
        self.assertEqual(f['a'], 'foo')

    def test_setitem_no_key(self):
        try:
            self.field['h'] = 'error'
        except KeyError:
            pass
        except Exception as e:
            self.fail('Unexpected exception thrown: %s' % e)
        else:
            self.fail('KeyError not thrown')

    def test_setitem_repeated_key(self):
        try:
            self.field.add_subfield('a','bar')
            self.field['a'] = 'error'
        except KeyError:
            pass
        except Exception as e:
            self.fail('Unexpected exception thrown: %s' % e)
        else:
            self.fail('KeyError not thrown')

    def test_setitem(self):
        self.field['a'] = 'changed'
        self.assertEqual(self.field['a'], 'changed')



class SubjectFieldTest(unittest.TestCase):

    def setUp(self):
        self.subjectfield = Field(
            tag = '650',
            indicators = [' ', '0'],
            subfields = [
                'a', 'Python (Computer program language)',
                'v', 'Poetry.'
            ]
        )

    def test_is_subject_field(self):
        self.assertEqual(self.subjectfield.is_subject_field(), True)
        self.assertEqual(self.field.is_subject_field(), False)

    def test_format_field(self):
        self.subjectfield.add_subfield('6', '880-4')
        self.assertEqual(self.subjectfield.format_field(),
            'Python (Computer program language) -- Poetry.')
        self.field.add_subfield('6', '880-1')
        self.assertEqual(self.field.format_field(),
            'Huckleberry Finn:  An American Odyssey')


def suite():
    return unittest.TestSuite((
        unittest.makeSuite(ControlFieldTest, 'test'),
        unittest.makeSuite(FieldTest, 'test'),
        unittest.makeSuite(FieldIndicatorsTest, 'test'),
        ))

if __name__ == "__main__":
    unittest.main()


