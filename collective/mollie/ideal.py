import httplib
import urllib

from elementtree import ElementTree as ET
from zope.interface import implements

from collective.mollie.interfaces import IMollieIdeal


class MollieIdeal(object):
    """A utility that wraps the Mollie iDeal API."""
    implements(IMollieIdeal)

    API_HOST = 'secure.mollie.nl'
    BASE_PATH = '/xml/ideal'

    def _do_request(self, data={}, testmode=False):
        """Call the Mollie API, send ``data`` and return the resulting XML.

        The ``data`` parameter is a dictionary with parameters to send
        to the Mollie API.

        If ``testmode`` is True, a flag is sent along with the request
        to signal this is a test.
        """
        connection = httplib.HTTPSConnection(self.API_HOST)
        if testmode:
            data['testmode'] = 'true'
        encoded_data = urllib.urlencode(data)
        connection.request(
            'POST', self.BASE_PATH, encoded_data,
            {'Content-type': 'application/x-www-form-urlencoded'})
        return connection.getresponse().read()

    def get_banks(self, testmode=False):
        """Return a list of bank id and name tuples.

        Example: [('0031, 'ABN AMRO'), ('0721', 'Postbank')]

        The ``testmode`` determines whether we get the actual list of
        banks or only the test bank 'The Big Mollie Bank'.
        """
        data = {'a': 'banklist'}
        answer = self._do_request(data, testmode)
        parsed_xml = ET.XML(answer)
        result = []
        for bank in parsed_xml.getiterator('bank'):
            bank_id = bank.find('bank_id').text
            bank_name = bank.find('bank_name').text
            result.append((bank_id, bank_name))
        return result

    def request_payment(self, partner_id, bank_id, amount, message, report_url,
                        return_url, profile_key=None, testmode=False):
        """Return transaction ID and URL to visit.

        To send the request, a ``partner_id``, the Mollie account number,
        is needed.

        Furthermore, the ``bank_id``, ``amount`` and ``message`` are
        obviously needed. Note that the ``amount`` is in **cents** and
        the ``message`` can only be 29 characters (any more characters
        are ignored).

        The ``report_url`` is used by Mollie to report that the status
        of the transaction can be requested. The ``return_url`` is
        where the customer will be redirected to after the payment is
        completed (either successfully or not).

        Optionally, the ``profile_key`` can be used to select another
        profile than the default profile for the ``partnerid``.
        """
        data = {
            'a': 'fetch',
            'partnerid': partner_id,
            'amount': amount,
            'bank_id': bank_id,
            'description': message,
            'reporturl': report_url,
            'returnurl': return_url,
        }
        if profile_key:
            data['profile_key'] = profile_key
        answer = self._do_request(data, testmode=testmode)
        order = ET.XML(answer).find('order')
        transaction_id = order.find('transaction_id').text
        confirm_amount = order.find('amount').text
        confirm_currency = order.find('currency').text
        url = order.find('URL').text
        if confirm_amount != amount:
            raise ValueError('The amount for the payment is incorrect.')
        if confirm_currency != 'EUR':
            raise ValueError('The currency for the payment is incorrect.')
        return transaction_id, url

    def check_payment(self, partner_id, transaction_id, testmode=False):
        """Check the status of the payment and return a dict with infomation.

        With a Mollie account number, ``partner_id``, and the ID of a
        transaction, ``transaction_id``, you can retieve the state of
        said transaction.

        The content of the return value depends on the status of the payment.

        If, and only if, the payment succeeded, the return value also
        contains information about consumer that payed.

        Note that if you call this method too early and the state is
        still 'Open' you are effectively never able to check the final
        state of the transaction. This is because the status may only
        be retrieved ONCE! Subsequent checks will always return a
        status 'CheckedBefore' and appear not payed.

        In other words: way until Mollie pinged the ``report_url``
        which was sent with the ``request_payment`` method.
        """
        data = {
            'a': 'check',
            'partnerid': partner_id,
            'transaction_id': transaction_id,
        }
        answer = self._do_request(data, testmode=testmode)
        order_xml = ET.XML(answer).find('order')
        result = {
            'transaction_id': order_xml.find('transaction_id').text,
            'amount': order_xml.find('amount').text,
            'currency': order_xml.find('currency').text,
            'payed': ('true' == order_xml.find('payed').text),
            'status': order_xml.find('status').text,
        }
        consumer_xml = order_xml.find('consumer')
        if consumer_xml:
            result.update({
                'consumer_name': consumer_xml.find('consumerName').text,
                'consumer_account': consumer_xml.find('consumerAccount').text,
                'consumer_city': consumer_xml.find('consumerCity').text,
            })
        return result
