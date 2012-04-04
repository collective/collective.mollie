import os
import unittest2 as unittest

from mock import MagicMock

from zope.component import eventtesting
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.publisher.browser import TestRequest

from collective.mollie.adapter import MollieIdealPayment
from collective.mollie.ideal import MollieAPIError
from collective.mollie.interfaces import IMollieIdeal
from collective.mollie.interfaces import IMollieIdealPayment
from collective.mollie.interfaces import IMollieIdealPaymentEvent
from collective.mollie.testing import COLLECTIVE_MOLLIE_INTEGRATION_TESTING
from collective.mollie.testing import Foo


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

    def test_banklist_request(self):
        """Make sure we send the right parameters to Mollie"""
        def side_effect(*args, **kwargs):
            return mock_do_request('banks.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        self.ideal.get_banks()
        self.ideal._do_request.assert_called_with({'a': 'banklist'})

    def test_banklist(self):
        """Check the list of banks."""
        def side_effect(*args, **kwargs):
            return mock_do_request('banks.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        banks = self.ideal.get_banks()
        self.assertTrue(('0021', 'Rabobank') in banks)

    def test_basic_payment_request_request(self):
        """Make sure we send the right parameters to Mollie"""
        def side_effect(*args, **kwargs):
            return mock_do_request('request_payment_good.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        self.ideal.request_payment(
            self.partner_id, self.bank_id, self.amount, self.message,
            self.report_url, self.return_url)
        self.ideal._do_request.assert_called_with(
            {'a': 'fetch', 'partnerid': self.partner_id, 'amount': self.amount,
            'bank_id': self.bank_id, 'description': self.message,
            'reporturl': self.report_url, 'returnurl': self.return_url
            })

    def test_basic_payment_request(self):
        """Check basic (successfull) payment request."""
        def side_effect(*args, **kwargs):
            return mock_do_request('request_payment_good.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        transaction_id, url = self.ideal.request_payment(
            self.partner_id, self.bank_id, self.amount, self.message,
            self.report_url, self.return_url)
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

    def test_payment_request_amount_int(self):
        """Check that the amount can also be an int."""
        def side_effect(*args, **kwargs):
            return mock_do_request('request_payment_good.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        transaction_id, url = self.ideal.request_payment(
            self.partner_id, self.bank_id, int(self.amount), self.message,
            self.report_url, self.return_url)
        # The fact that no error was raised proves that the amount was correct.
        self.assertTrue(transaction_id == '482d599bbcc7795727650330ad65fe9b')

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

    def test_payment_request_too_low_amount(self):
        """Check payment request with too low amount."""
        def side_effect(*args, **kwargs):
            return mock_do_request('error_14.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)

        # We expect an error because the amount it too low.
        self.assertRaises(MollieAPIError, self.ideal.request_payment,
            self.partner_id, self.bank_id, 1, self.message,
            self.report_url, self.return_url)

    def test_check_payment_request(self):
        """Make sure we send the right parameters to Mollie."""
        def side_effect(*args, **kwargs):
            return mock_do_request('payment_success.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        self.ideal.check_payment(self.partner_id, self.transaction_id)
        self.ideal._do_request.assert_called_with(
            {'a': 'check',
             'partnerid': self.partner_id,
             'transaction_id': self.transaction_id,
            })

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
        self.assertTrue(result['paid'])
        self.assertTrue('consumer' in result)
        self.assertTrue(result['consumer']['name'] == 'T. TEST')
        self.assertTrue(result['consumer']['account'] == '0123456789')
        self.assertTrue(result['consumer']['city'] == 'Testdorp')
        self.assertTrue(result['status'] == 'Success')

    def test_check_payment_open(self):
        """Check payment which is still open."""
        def side_effect(*args, **kwargs):
            return mock_do_request('payment_open.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        result = self.ideal.check_payment(self.partner_id, self.transaction_id)
        self.assertTrue(result['paid'] == False)
        self.assertTrue(result['status'] == 'Open')
        self.assertTrue('consumer_name' not in result)

    def test_check_payment_checked_before(self):
        """Check payment which has been checked before."""
        def side_effect(*args, **kwargs):
            return mock_do_request('payment_checked_before.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        result = self.ideal.check_payment(self.partner_id, self.transaction_id)
        self.assertTrue(result['paid'] == False)
        self.assertTrue(result['status'] == 'CheckedBefore')
        self.assertTrue('consumer_name' not in result)

    def test_check_payment_cancelled(self):
        """Check payment which has been checked before."""
        def side_effect(*args, **kwargs):
            return mock_do_request('payment_cancelled.xml')
        self.ideal._do_request = MagicMock(
            side_effect=side_effect)
        result = self.ideal.check_payment(self.partner_id, self.transaction_id)
        self.assertTrue(result['paid'] == False)
        self.assertTrue(result['status'] == 'Cancelled')
        self.assertTrue('consumer_name' not in result)


class TestPaymentAdapter(unittest.TestCase):
    """Test the Mollie iDeal Payment adapter."""

    layer = COLLECTIVE_MOLLIE_INTEGRATION_TESTING

    def setUp(self):
        self.foo = Foo()
        self.adapted = IMollieIdealPayment(self.foo)
        self.adapted.ideal_wrapper.old_do_request = \
            self.adapted.ideal_wrapper._do_request
        self.partner_id = '999999'
        self.bank_id = '9999'
        self.amount = '123'  # 1.23 Euro
        self.currency = 'EUR'
        self.message = 'Testing payment'
        self.report_url = 'http://example.com/report_payment'
        self.return_url = 'http://example.com/return_url'
        self.transaction_id = '482d599bbcc7795727650330ad65fe9b'

    def tearDown(self):
        self.adapted.ideal_wrapper._do_request = \
            self.adapted.ideal_wrapper.old_do_request

    def test_adapter(self):
        """Test whether we can adapt."""
        self.assertTrue(isinstance(self.adapted, MollieIdealPayment))

    def test_get_banks(self):
        """Check we can retrieve the banks from Mollie."""
        def side_effect(*args, **kwargs):
            return mock_do_request('banks.xml')
        self.adapted.ideal_wrapper._do_request = MagicMock(
            side_effect=side_effect)
        banks = self.adapted.get_banks()
        self.assertTrue(('0021', 'Rabobank') in banks)

    def test_get_payment_url(self):
        """Check we can get a payment URL and the transaction ID is stored."""
        def side_effect(*args, **kwargs):
            return mock_do_request('request_payment_good.xml')
        self.adapted.ideal_wrapper._do_request = MagicMock(
            side_effect=side_effect)
        url = self.adapted.get_payment_url(self.partner_id, self.bank_id,
            self.amount, self.message, self.report_url, self.return_url)
        # The right URL is returned
        self.assertTrue(url == 'https://mijn.postbank.nl/internetbankieren/' +
                               'SesamLoginServlet?sessie=ideal&trxid=' +
                               '003123456789123&random=123456789abcdefgh')
        # The right transaction information is stored.
        self.assertTrue(self.adapted.transaction_id == self.transaction_id)
        self.assertTrue(self.adapted.amount == self.amount)
        self.assertTrue(self.adapted._partner_id == self.partner_id)

    def test_get_payment_status_success(self):
        """Check the best case: a successfull payment."""
        def side_effect(*args, **kwargs):
            return mock_do_request('request_payment_good.xml')
        self.adapted.ideal_wrapper._do_request = MagicMock(
            side_effect=side_effect)
        self.adapted.get_payment_url(self.partner_id, self.bank_id,
            self.amount, self.message, self.report_url, self.return_url)

        def side_effect2(*args, **kwargs):
            return mock_do_request('payment_success.xml')
        self.adapted.ideal_wrapper._do_request = MagicMock(
            side_effect=side_effect2)
        result = self.adapted.get_payment_status()
        self.assertTrue(result == 'Success')
        self.assertTrue(self.adapted.paid)
        self.assertTrue(self.adapted.consumer['name'] == 'T. TEST')
        self.assertTrue(self.adapted.consumer['account'] == '0123456789')
        self.assertTrue(self.adapted.consumer['city'] == 'Testdorp')
        self.assertTrue(self.adapted.status == 'Success')
        self.assertTrue(self.adapted.last_status == 'Success')

    def test_get_payment_status_cancelled(self):
        """Check a cancelled payment."""
        def side_effect(*args, **kwargs):
            return mock_do_request('request_payment_good.xml')
        self.adapted.ideal_wrapper._do_request = MagicMock(
            side_effect=side_effect)
        self.adapted.get_payment_url(self.partner_id, self.bank_id,
            self.amount, self.message, self.report_url, self.return_url)

        def side_effect2(*args, **kwargs):
            return mock_do_request('payment_cancelled.xml')
        self.adapted.ideal_wrapper._do_request = MagicMock(
            side_effect=side_effect2)
        self.adapted.get_payment_status()
        self.assertFalse(self.adapted.paid)
        self.assertTrue(self.adapted.consumer is None)
        self.assertTrue(self.adapted.status == 'Cancelled')

    def test_get_payment_status_checked_before(self):
        """Check payment twice: teh result is saved."""
        def side_effect(*args, **kwargs):
            return mock_do_request('request_payment_good.xml')
        self.adapted.ideal_wrapper._do_request = MagicMock(
            side_effect=side_effect)
        self.adapted.get_payment_url(self.partner_id, self.bank_id,
            self.amount, self.message, self.report_url, self.return_url)

        # We first check the success.
        def side_effect2(*args, **kwargs):
            return mock_do_request('payment_success.xml')
        self.adapted.ideal_wrapper._do_request = MagicMock(
            side_effect=side_effect2)
        result = self.adapted.get_payment_status()
        self.assertTrue(result == 'Success')

        # A second check will return 'CheckedBefore' but the payment
        # status will be saved.
        def side_effect3(*args, **kwargs):
            return mock_do_request('payment_checked_before.xml')
        self.adapted.ideal_wrapper._do_request = MagicMock(
            side_effect=side_effect3)
        result = self.adapted.get_payment_status()
        self.assertTrue(result == 'CheckedBefore')
        self.assertTrue(self.adapted.paid)
        self.assertTrue(self.adapted.status == 'Success')
        self.assertTrue(self.adapted.last_status == 'CheckedBefore')


class TestReportView(unittest.TestCase):

    layer = COLLECTIVE_MOLLIE_INTEGRATION_TESTING

    def _side_effect(*args, **kwargs):
        return mock_do_request('payment_success.xml')

    def setUp(self):
        self.ideal = getUtility(IMollieIdeal)
        self.ideal.old_do_request = self.ideal._do_request
        self.ideal._do_request = MagicMock(
            side_effect=self._side_effect)

        self.foo = Foo()
        self.adapted = IMollieIdealPayment(self.foo)
        self.adapted._partner_id = '999999'
        self.adapted.transaction_id = '482d599bbcc7795727650330ad65fe9b'
        eventtesting.setUp()

    def tearDown(self):
        self.ideal._do_request = self.ideal.old_do_request
        eventtesting.clearEvents()

    def test_missing_transaction_id(self):
        """Check missing transaction_id is invalid."""
        request = TestRequest()
        report_payment_view = getMultiAdapter((self.foo, request),
                                              name='report_payment_status')
        result = report_payment_view()
        self.assertTrue(result == 'Wrong or missing transaction ID')
        self.assertTrue(request.response.getStatus() == 403)

    def test_wrong_transaction_id(self):
        """Check wrong transaction_id is invalid."""
        request = TestRequest(form=dict(transaction_id='deadbeef'))
        report_payment_view = getMultiAdapter((self.foo, request),
                                              name='report_payment_status')
        result = report_payment_view()
        self.assertTrue(result == 'Wrong or missing transaction ID')
        self.assertTrue(request.response.getStatus() == 403)

    def test_correct_response(self):
        """Check the response if the right transaction_id is received."""
        request = TestRequest(
            form=dict(transaction_id=self.adapted.transaction_id))
        report_payment_view = getMultiAdapter((self.foo, request),
                                              name='report_payment_status')
        result = report_payment_view()
        self.assertTrue(result == 'OK')
        self.assertTrue(request.response.getStatus() == 200)

    def test_correct_processing(self):
        """Check the payment has indeed been processed."""
        request = TestRequest(
            form=dict(transaction_id=self.adapted.transaction_id))
        report_payment_view = getMultiAdapter((self.foo, request),
                                              name='report_payment_status')
        report_payment_view()
        self.assertTrue(self.adapted.paid)

    def test_payment_event(self):
        """Check that the MollieIdealPaymentEvent was fired."""
        request = TestRequest(
            form=dict(transaction_id=self.adapted.transaction_id))
        report_payment_view = getMultiAdapter((self.foo, request),
                                              name='report_payment_status')
        report_payment_view()
        payment_events = [event for event in eventtesting.getEvents()
                          if IMollieIdealPaymentEvent.providedBy(event)]
        self.assertTrue(len(payment_events) > 0)
