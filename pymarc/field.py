# -*- coding: utf-8 -*-

"The pymarc.field file."

from pymarc.constants import SUBFIELD_INDICATOR, END_OF_FIELD
from pymarc.marc8 import marc8_to_unicode
from pymarc.exceptions import PymarcException



extra_controlfield_tags = {}



class __BaseField:


    def __init__(self, tag, data):

        if type(tag) != type(data):
            raise PymarcException(
                "{}: Tag and data types should be the same, got '{}' and '{}'"
                .format(
                self.__class__.__name__, type(tag).__name__, type(data).__name__
                ))

        if not isinstance(data, (str, bytes)):
            raise PymarcException(
                "{}: Invalid input type - '{}', should be 'str' or 'bytes'.".format(
                self.__class__.__name__, type(data).__name__
                ))

        self.data_type = type(data)
        self.tag = tag


    def get_tag(self):
        return self._tag


    def set_tag(self, tag):
        if not isinstance(tag, self.data_type):
            raise PymarcException(
                "{}: Invalid tag type - '{}', expected - '{}'".format(
                self.__class__.__name__, type(tag).__name__,
                self.data_type.__name__
                ))
        # normalize tag if needed
        while len(tag) < 3:
            prefix = '0' if isinstance(tag, str) else b'0'
            tag = prefix + tag
        self._tag = tag


    tag = property(get_tag, set_tag, None, "Control field tag as bytes.")



class ControlField(__BaseField):
    """
    ByteControlField() pass in the field tag and field data as bytes.

        field = ControlField(tag=b'001', data=b'fol05731351')
    or
        field = ControlField(b'001', b'fol05731351')
    """


    def __init__(self, tag, data):
        super(ControlField, self).__init__(tag, data)
        self.data = data


    def get_data(self):
        return self._data

    value = get_data


    def set_data(self, data):
        if not isinstance(data, self.data_type):
            raise PymarcException(
                "{}: Invalid value type - '{}', expected - '{}'".format(
                self.__class__.__name__, type(data).__name__,
                self.data_type.__name__))
        self._data = data


    data = property(get_data, set_data, None, "ControlField value.")


    def decode(self, encoding="latin-1", errors="strict"):
        if isinstance(self._data, bytes):
            return self._data.decode(encoding=encoding, errors=errors)
        else:
            return self._data


    def as_marc(self):
        """
        used during conversion of a field to raw marc
        """
        if isinstance(self._data, bytes):
            return self._data + END_OF_FIELD
        else:
            return self._data.encode(encoding="latin-1", errors="strict"
                                ) + END_OF_FIELD

    # alias for backwards compatibility
    as_marc21 = as_marc


    def __str__(self):
        """
        A ControlField object in a string context will return the tag
        and value as a string. This follows MARCMaker format; see [1]
        and [2] for further reference. Special character mnemonic strings
        have yet to be implemented (see [3]), so be forewarned. Note also
        for complete MARCMaker compatibility, you will need to change your
        newlines to DOS format ('\r\n').

        [1] http://www.loc.gov/marc/makrbrkr.html#mechanics
        [2] http://search.cpan.org/~eijabb/MARC-File-MARCMaker/
        [3] http://www.loc.gov/marc/mnemonics.html
        """
        if isinstance(self._data, bytes):
            text = '={}  {}'.format(
                    self.tag.decode(encoding="latin-1"),
                    self._data.decode(encoding="latin-1").replace(' ','\\')
                )
        else:
            text = '={}  {}'.format(
                    self.tag, self._data.replace(' ','\\')
                )
        return text



class Field(__BaseField):
    """
    Field() pass in the field tag, indicators and subfields for the tag.

        field = Field(
            tag = '245',
            indicators = ['0','1'],
            subfields = [
                'a', 'The pragmatic programmer : ',
                'b', 'from journeyman to master /',
                'c', 'Andrew Hunt, David Thomas.',
            ]

    """
    def __init__(self, tag, indicators=None, subfields=None):
        super(Field, self).__init__(tag, tag)
        self.indicators = indicators
        self.subfields = subfields or []


    def get_indicators(self):
        return self._indicators


    def set_indicators(self, indicators):
        if not indicators:
            if self.data_type == bytes:
                self._indicators = b"  "
            else:
                self._indicators = "  "
        else:
            if isinstance(indicators, (list, tuple)):
                if len(indicators) == 2:
                    ind = '' if self.data_type == str else b''
                    for i in indicators:
                        if isinstance(i, self.data_type) or i is None:
                            ind += i or (' ' if self.data_type == str else b' ')
                        elif isinstance(i, int):
                            ind += str(i) if self.data_type == str else bytes(str(i), 'ascii')
                        else:
                            raise PymarcException(
                                "{}: Bad indicator type ('{}'), expected '{}'"
                                .format(
                                self.__class__.__name__,
                                type(i).__name__, self.data_type.__name__))
                else:
                    raise PymarcException(
                        "{}: Bad indicators number: {:d}, expected 2".format(
                        self.__class__.__name__, len(indicators)))
            else:
                ind = indicators[:]
            if isinstance(ind, self.data_type):
                if len(ind) == 2:
                    self._indicators = ind
                else:
                    raise PymarcException(
                        "{}: Bad indicators number: {:d}, expected 2".format(
                        self.__class__.__name__, len(ind)))
            else:
                raise PymarcException(
                    "{}: Bad indicators type ('{}'), expected '{}'".format(
                    self.__class__.__name__,
                    type(ind).__name__, self.data_type.__name__))
        self.indicator1 = self._indicators[:1]
        self.indicator2 = self._indicators[1:]


    indicators = property(get_indicators, set_indicators, None, "Field indicators.")


    def get_all_subfields(self):
        return self._subfields


    def set_subfields(self, subfields):
        self._subfields = []
        if not subfields:
            return
        elif isinstance(subfields[0], (str, bytes)):
            # this is a flat list of codes and field data
            if len(subfields) % 2 != 0:
                raise PymarcException(
                    "{}: Flat list of subfields should have even"
                    " number of elements.".format(self.__class__.__name__))
            for i in range(0,len(subfields),2):
                self.add_subfield(subfields[i], subfields[i + 1])
        elif isinstance(subfields[0], (list, tuple)):
            for code, value in subfields:
                self.add_subfield(code, value)


    subfields = property(get_all_subfields, set_subfields, None, "Subfields")


    def __iter__(self):
        self.__pos = 0
        return self


    def __next__(self):
        "Needed for iteration."
        while self.__pos < len(self._subfields):
            subfield = self._subfields[ self.__pos ]
            self.__pos += 1
            return subfield
        raise StopIteration


    def __getitem__(self, code):
        """
        Retrieve the first subfield with a given subfield code in a field:

            field['a']

        Handy for quick lookups.
        """
        subfields = self.get_subfields(code)
        if len(subfields) > 0:
            return subfields[0]
        return None


    def __contains__(self, code):
        """
        Allows a shorthand test of field membership:

            'a' in field

        """
        subfields = self.get_subfields(code)
        return len(subfields) > 0


    def __setitem__(self, code, value):
        """
        Set the values of the subfield code in a field:

            field['a'] = 'value'

        Raises KeyError if there is more than one subfield code.
        """
        ids = [idx for idx, (c, v) in enumerate(self._subfields) if code == c]
        if len(ids) > 1:
            raise KeyError("{}: more than one code '{}'".format(
                self.__class__.__name__, code))
        elif len(ids) == 0:
            raise KeyError("{}: no code '{}'".format(
                self.__class__.__name__, code))
        self._subfields[ids[0]][1] = value


    def get_subfields(self, *codes):
        """
        get_subfields() accepts one or more subfield codes and returns
        a list of subfield values.  The order of the subfield values
        in the list will be the order that they appear in the field.

            print field.get_subfields('a')
            print field.get_subfields('a', 'b', 'z')
        """
        values = []
        for code, value in self._subfields:
            if code in codes:
                values.append(value)
        return values


    def add_subfield(self, code, value):
        """
        Adds a subfield code/value pair to the field.

            field.add_subfield('u', 'http://www.loc.gov')
        """
        if not isinstance(value, self.data_type):
            raise PymarcException(
                "{}: Invalid value type - '{}', should be {}."
                .format(self.__class__.__name__,
                type(value).__name__, self.data_type.__name__
                ))

        if type(code) != type(value):
            raise PymarcException(
                "{}: Code and value types should be the same, got '{}' and '{}'"
                .format(
                self.__class__.__name__,
                type(code).__name__, type(value).__name__
                ))

        self._subfields.append([code, value])


    def delete_subfield(self, acode):
        """
        Deletes the first subfield with the specified 'code' and returns
        its value:

            field.delete_subfield('a')

        If no subfield is found with the specified code None is returned.
        """
        for idx, (code, value) in enumerate(self._subfields):
            if acode == code:
                self._subfields.pop(idx)
                return value
        return None


    def as_marc(self):
        """
        used during conversion of a field to raw marc
        """
        if self.data_type == bytes:
            marc = self.indicators
            for code, value in self._subfields:
                marc += SUBFIELD_INDICATOR + code + value
        else:
            marc = self.indicators.encode("utf-8")
            for code, value in self._subfields:
                marc += SUBFIELD_INDICATOR + code.encode("utf-8") + value.encode("utf-8")
        return marc + END_OF_FIELD


    # alias for backwards compatibility
    as_marc21 = as_marc


    def __str__(self):
        """
        A Field object in a string context will return the tag, indicators
        and subfield as a string. This follows MARCMaker format; see [1]
        and [2] for further reference. Special character mnemonic strings
        have yet to be implemented (see [3]), so be forewarned. Note also
        for complete MARCMaker compatibility, you will need to change your
        newlines to DOS format ('\r\n').

        [1] http://www.loc.gov/marc/makrbrkr.html#mechanics
        [2] http://search.cpan.org/~eijabb/MARC-File-MARCMaker/
        [3] http://www.loc.gov/marc/mnemonics.html
        """
        if self.data_type == bytes:
            tag = self.tag.decode("latin-1")
            indicators = self.indicators.decode("latin-1")
        else:
            tag = self.tag
            indicators = self.indicators

        text = '={}  {}'.format(tag, indicators.replace(' ','\\'))

        for code, value in self._subfields:
            if self.data_type == bytes:
                code = code.decode("latin-1")
                value = value.decode("latin-1")
            text += '${}{}'.format(code, value)

        return text


    def value(self):
        """
        Returns the field as a string or bytes without tag, indicators, and
        subfield indicators.
        """
        value_list = []
        for code, value in self._subfields:
            value_list.append(value.strip())
        if self.data_type == bytes:
            return b' '.join(value_list)
        else:
            return ' '.join(value_list)


    def format_field(self):
        """
        Returns the field as a string without tag, indicators, and
        subfield indicators. Like pymarc.Field.value(), but prettier
        (adds spaces, formats subject headings).
        """
        fielddata = ''
        for code, value in self._subfields:
            if code in ('6', b'6'):
                continue
            if not self.is_subject_field():
                fielddata += ' {}'.format(value)
            else:
                if code not in ('v', 'x', 'y', 'z', b'v', b'x', b'y', b'z'):
                    fielddata += ' {}'.format(value)
                else:
                    fielddata += ' -- {}'.format(value)

        return fielddata.strip()


    def is_subject_field(self):
        """
        Returns True or False if the field is considered a subject
        field.  Used by format_field.
        """
        return self.tag[0] in ('6',  b'6')



def map_marc8_field(f):
    if f.is_control_field():
        f.data = marc8_to_unicode(f.data)
    else:
        f.subfields = map(marc8_to_unicode, f.subfields)
    return f
