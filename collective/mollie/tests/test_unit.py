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
        self.currency = 'EUR'
        self.message = 'Testing payment'
        self.report_url = 'http://example.com/report_payment'
        self.return_url = 'http://example.com/return_url'
        self.transaction_id = '482d599bbcc7795727650330ad65fe9b'

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
            return mock_do_request('request_payment_good.xml')
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

    def test_payment_request_wrong_amount(self):
        """Check payment request with wrong amount in answer"""
        def side_effect(*args, **kwargs):
            return mock_do_request('request_payment_wrong_amount.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)

        # We expect an error because the amount is wrong.
        self.assertRaises(ValueError, self.ideal.request_payment,
            self.partner_id, self.bank_id, self.amount, self.message,
            self.report_url, self.return_url)

    def test_payment_request_wrong_currency(self):
        """Check payment request with wrong currency in answer"""
        def side_effect(*args, **kwargs):
            return mock_do_request('request_payment_wrong_currency.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)

        # We expect an error because the currency is wrong.
        self.assertRaises(ValueError, self.ideal.request_payment,
            self.partner_id, self.bank_id, self.amount, self.message,
            self.report_url, self.return_url)

    def test_check_payment_request(self):
        """Make sure we send the right parameters to Mollie"""
        def side_effect(*args, **kwargs):
            return mock_do_request('payment_success.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        self.ideal.check_payment(self.partner_id, self.transaction_id)
        self.ideal._do_request.assert_called_with(
            {'a': 'check',
             'partnerid': self.partner_id,
             'transaction_id': self.transaction_id,
            },
            testmode=False
        )

    def test_check_payment_success(self):
        """Check the best case: a successfull payment."""
        def side_effect(*args, **kwargs):
            return mock_do_request('payment_success.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        result = self.ideal.check_payment(self.partner_id, self.transaction_id)
        self.assertTrue(result['transaction_id'] == self.transaction_id)
        self.assertTrue(result['amount'] == self.amount)
        self.assertTrue(result['currency'] == self.currency)
        self.assertTrue(result['payed'])
        self.assertTrue(result['consumer_name'] == 'T. TEST')
        self.assertTrue(result['consumer_account'] == '0123456789')
        self.assertTrue(result['consumer_city'] == 'Testdorp')
        self.assertTrue(result['status'] == 'Success')

    def test_check_payment_open(self):
        """Check payment which is still open."""
        def side_effect(*args, **kwargs):
            return mock_do_request('payment_open.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        result = self.ideal.check_payment(self.partner_id, self.transaction_id)
        self.assertTrue(result['payed'] == False)
        self.assertTrue(result['status'] == 'Open')
        self.assertTrue('consumer_name' not in result)

    def test_check_payment_checked_before(self):
        """Check payment which has been checked before."""
        def side_effect(*args, **kwargs):
            return mock_do_request('payment_checked_before.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        result = self.ideal.check_payment(self.partner_id, self.transaction_id)
        self.assertTrue(result['payed'] == False)
        self.assertTrue(result['status'] == 'CheckedBefore')
        self.assertTrue('consumer_name' not in result)

    def test_check_payment_cancelled(self):
        """Check payment which has been checked before."""
        def side_effect(*args, **kwargs):
            return mock_do_request('payment_cancelled.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        result = self.ideal.check_payment(self.partner_id, self.transaction_id)
        self.assertTrue(result['payed'] == False)
        self.assertTrue(result['status'] == 'Cancelled')
        self.assertTrue('consumer_name' not in result)
