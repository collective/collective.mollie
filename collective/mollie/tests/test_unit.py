import os
import unittest2 as unittest

from collective.mollie.xml_parser import ElementTree
from collective.mollie.xml_parser import XmlListConfig
from collective.mollie.xml_parser import XmlDictConfig
from collective.mollie.xml_parser import xml_string_to_dict


def get_xml_from_file(filename):
    """Return the XML stored in ``filename``."""
    current_location = os.path.dirname(__file__)
    xml_file = os.path.join(
        current_location, 'xml', filename)
    fp = open(xml_file, 'r')
    content = fp.read()
    fp.close()
    return content


class TestXmlListConfig(unittest.TestCase):
    """Test the XML -> list class."""

    def test_list(self):
        """Check conversion of simple XML to list."""
        xml = get_xml_from_file('list.xml')
        tree = ElementTree.XML(xml)
        xml_list = XmlListConfig(tree)
        self.assertEqual(xml_list, ['1', '2'])

    def test_list_in_list(self):
        """Check conversion of a list in a list."""
        xml = get_xml_from_file('list_in_list.xml')
        tree = ElementTree.XML(xml)
        xml_list = XmlListConfig(tree)
        self.assertEqual(xml_list, [['1', '2']])

    def test_lists_in_list(self):
        """Check conversion of lists in a list."""
        xml = get_xml_from_file('lists_in_list.xml')
        tree = ElementTree.XML(xml)
        xml_list = XmlListConfig(tree)
        self.assertEqual(xml_list, [['1', '2'], ['3', '4']])

    def test_two_root_elements(self):
        """Check XML can only have one root element."""
        xml = get_xml_from_file('two_root_elements.xml')
        self.assertRaises(ElementTree.ParseError, ElementTree.XML, xml)


class TestXmlDictConfig(unittest.TestCase):
    """Test the XML -> dict class"""

    def test_dict(self):
        """Check conversion of simple XML to dict."""
        xml = get_xml_from_file('dict.xml')
        tree = ElementTree.XML(xml)
        xml_dict = XmlDictConfig(tree)
        expected_dict = {'Bar': '1',
                         'Qux': '2'}
        self.assertEqual(xml_dict, expected_dict)

    def test_dict_in_dict(self):
        """Check conversion of a dict of dicts."""
        xml = get_xml_from_file('dict_in_dict.xml')
        tree = ElementTree.XML(xml)
        xml_dict = XmlDictConfig(tree)
        expected_dict = {'Bar': {'Qux': '1',
                                 'Quux': '2'}}
        self.assertEqual(xml_dict, expected_dict)

    def test_dicts_in_dict(self):
        """Check conversion of dicts in a dict."""
        xml = get_xml_from_file('dicts_in_dict.xml')
        tree = ElementTree.XML(xml)
        xml_dict = XmlDictConfig(tree)
        expected_dict = {'Bar': {'Qux': '1',
                                 'Quux': '2'},
                         'Corge': {'Qux': '3',
                                  'Quux': '4'}}
        self.assertEqual(xml_dict, expected_dict)

    def test_dict_with_attributes(self):
        """Check conversion with using attributes."""
        xml = get_xml_from_file('dict_attributes.xml')
        tree = ElementTree.XML(xml)
        xml_dict = XmlDictConfig(tree)
        expected_dict = {'level': 'root',
                         'Bar': {'value': '1'},
                         'Qux': {'eggs': '2',
                                 'Quux': {'ham': '3'},
                                 'Quuux': '4'},
                         'Corge': '5'}
        self.assertEqual(xml_dict, expected_dict)

    def test_two_root_elements(self):
        """Check XML can only have one root element."""
        xml = get_xml_from_file('two_root_elements.xml')
        self.assertRaises(ElementTree.ParseError, ElementTree.XML, xml)


class TestXmlCombinedConfig(unittest.TestCase):
    """Test combinations of dicts and lists."""

    def test_dict_in_list(self):
        """Check conversion of a dict inside a list."""
        xml = get_xml_from_file('dict_in_list.xml')
        tree = ElementTree.XML(xml)
        xml_list = XmlListConfig(tree)
        expected_list = [{'Qux': '1', 'Quux': '2'}]
        self.assertEqual(xml_list, expected_list)

    def test_list_in_dict(self):
        """Check conversion of a list inside a dict."""
        xml = get_xml_from_file('list_in_dict.xml')
        tree = ElementTree.XML(xml)
        xml_dict = XmlDictConfig(tree)
        expected_dict = {'Bar': {'Qux': ['1', '2']}}
        self.assertEqual(xml_dict, expected_dict)

    def test_dict_in_list_in_dict(self):
        """Check conversion a dict in a list inside a dict."""
        xml = get_xml_from_file('dict_in_list_in_dict.xml')
        tree = ElementTree.XML(xml)
        xml_dict = XmlDictConfig(tree)
        expected_dict = {'Bar': [{'Qux': '1',
                                  'Quux': '2'},
                                 {'Qux': '3',
                                  'Quux': '4',
                                  'Quuux': '5'}]}
        self.assertEqual(xml_dict, expected_dict)


class TestXmlStringToDict(unittest.TestCase):
    """Test the xml_string_to_dict helper function."""

    def test_dict(self):
        """Check conversion of simple XML to dict."""
        xml = get_xml_from_file('dict.xml')
        xml_dict = xml_string_to_dict(xml)
        expected_dict = {'Bar': '1',
                         'Qux': '2'}
        self.assertEqual(xml_dict, expected_dict)
