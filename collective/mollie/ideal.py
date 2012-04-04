import httplib
import urllib

from zope.interface import implements

from collective.mollie.interfaces import IMollieIdeal
from collective.mollie.xml_parser import XmlDictConfig
from collective.mollie.xml_parser import xml_string_to_dict


class MollieAPIError(EnvironmentError):
    """Error from the Mollie API"""


class MollieIdeal(object):
    """A utility that wraps the Mollie iDeal API."""
    implements(IMollieIdeal)

    API_HOST = 'secure.mollie.nl'
    BASE_PATH = '/xml/ideal'
    TESTMODE = False

    def _do_request(self, data={}):
        """Return XML after performing the actual call to the Mollie API.

        The ``data`` parameter is a dictionary with parameters to send
        to the Mollie API.

        If the TESTMODE flag is set to True, the request to Mollie
        will also contain the 'testmode' parameter (which will be set
        to 'true') to signal this is a test.

        The return value is a string.
        """
        connection = httplib.HTTPSConnection(self.API_HOST)
        if self.TESTMODE:
            data['testmode'] = 'true'
        encoded_data = urllib.urlencode(data)
        connection.request(
            'POST', self.BASE_PATH, encoded_data,
            {'Content-type': 'application/x-www-form-urlencoded'})
        return connection.getresponse().read()

    def _call_mollie(self, data,):
        """Call the Mollie API and return a dict with the result.

        The ``data`` dict should contain all the parameters we will
        send to Mollie.

        """
        result_str = self._do_request(data)
        result_dict = xml_string_to_dict(result_str)
        if 'item' in result_dict and \
           result_dict['item'].get('type') == 'error':
            raise MollieAPIError(result_dict['item']['errorcode'],
                                 result_dict['item']['message'])
        return result_dict

    def get_banks(self):
        """Return a list of bank id and name tuples.

        Example: [('0031, 'ABN AMRO'), ('0721', 'Postbank')]
        """
        data = {'a': 'banklist'}
        answer = self._call_mollie(data)
        banks = answer.get('bank', None)
        if not banks:
            return []
        elif isinstance(banks, XmlDictConfig):
            banks = [banks]
        return [(b['bank_id'], b['bank_name']) for b in banks]

    def request_payment(self, partner_id, bank_id, amount, message, report_url,
                        return_url, profile_key=None):
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
        answer = self._call_mollie(data)
        order = answer.get('order')
        if order.get('amount') != str(amount):
            raise ValueError('The amount for the payment is incorrect.')
        if order.get('currency') != 'EUR':
            raise ValueError('The currency for the payment is incorrect.')
        return order.get('transaction_id'), order.get('URL')

    def check_payment(self, partner_id, transaction_id):
        """Check the status of the payment and return a dict with infomation.

        With a Mollie account number, ``partner_id``, and the ID of a
        transaction, ``transaction_id``, you can retieve the state of
        said transaction.

        The content of the return value depends on the status of the payment.

        If, and only if, the payment succeeded, the return value also
        contains information about consumer that paid.

        Note that if you call this method too early and the state is
        still 'Open' you are effectively never able to check the final
        state of the transaction. This is because the status may only
        be retrieved ONCE! Subsequent checks will always return a
        status 'CheckedBefore' and appear not paid.

        In other words: way until Mollie pinged the ``report_url``
        which was sent with the ``request_payment`` method.
        """
        data = {
            'a': 'check',
            'partnerid': partner_id,
            'transaction_id': transaction_id,
        }
        answer = self._call_mollie(data)
        order = answer['order']
        if order.get('payed') == 'true':
            order['paid'] = True
        else:
            order['paid'] = False
        del order['payed']
        if order.get('consumer'):
            # 'Normalize' keys
            mapping = [('consumerName', 'name'),
                       ('consumerAccount', 'account'),
                       ('consumerCity', 'city')]
            for old, new in mapping:
                order['consumer'][new] = order['consumer'][old]
                del order['consumer'][old]
        return order
