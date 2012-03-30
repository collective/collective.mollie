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
