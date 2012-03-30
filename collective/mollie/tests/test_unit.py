import os
import unittest2 as unittest

from mock import MagicMock

from zope.component import getUtility

from collective.mollie.testing import COLLECTIVE_MOLLIE_INTEGRATION_TESTING
from collective.mollie.interfaces import IMollieIdeal


def mock_do_request(filename):
    """Return the XML stored in ``filename``."""
    current_location = os.path.dirname(__file__)
    xml_file = os.path.join(
        current_location, 'responses', filename)
    fp = open(xml_file, 'r')
    content = fp.read()
    fp.close()
    return content


class TestIdealWrapper(unittest.TestCase):
    """Unit test the iDeal wrapper without connecting to Mollie."""

    layer = COLLECTIVE_MOLLIE_INTEGRATION_TESTING

    def setUp(self):
        self.ideal = getUtility(IMollieIdeal)
        self.ideal.old_do_request = self.ideal._do_request
        self.partner_id = '999999'
        self.bank_id = '9999'
        self.amount = '123'  # 1.23 Euro
        self.message = 'Testing payment'
        self.report_url = 'http://example.com/report_payment'
        self.return_url = 'http://example.com/return_url'

    def tearDown(self):
        self.ideal._do_request = self.ideal.old_do_request

    def test_banklist(self):
        """Check the list of banks."""
        # Setup the mock _do_request to return the right XML
        def side_effect(*args, **kwargs):
            return mock_do_request('banks.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)

        banks = self.ideal.get_banks()
        # Make sure we are sending the right parameters.
        self.ideal._do_request.assert_called_with({'a': 'banklist'}, False)
        # Make sure the result is parsed properly
        self.assertTrue(('0021', 'Rabobank') in banks)

    def test_basic_payment_request(self):
        """Check basic (successfull) payment request."""
        # Setup the mock _do_request to return the right XML
        def side_effect(*args, **kwargs):
            return mock_do_request('payment_request_good.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)

        transaction_id, url = self.ideal.request_payment(
            self.partner_id, self.bank_id, self.amount, self.message,
            self.report_url, self.return_url)

        # Make sure we are sending the right parameters.
        self.ideal._do_request.assert_called_with(
            {'a': 'fetch', 'partnerid': self.partner_id, 'amount': self.amount,
            'bank_id': self.bank_id, 'description': self.message,
            'reporturl': self.report_url, 'returnurl': self.return_url
            },
            testmode=False)

        # Make sure the result is parsed properly
        self.assertTrue(transaction_id == '482d599bbcc7795727650330ad65fe9b')
        self.assertTrue(url == 'https://mijn.postbank.nl/internetbankieren/' +
                               'SesamLoginServlet?sessie=ideal&trxid=' +
                               '003123456789123&random=123456789abcdefgh')
