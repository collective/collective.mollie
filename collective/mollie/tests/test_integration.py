import unittest2 as unittest

from zope.component import getUtility

from collective.mollie.testing import COLLECTIVE_MOLLIE_INTEGRATION_TESTING
from collective.mollie.interfaces import IMollieIdeal


class TestIdealWrapper(unittest.TestCase):

    layer = COLLECTIVE_MOLLIE_INTEGRATION_TESTING

    def setUp(self):
        self.ideal = getUtility(IMollieIdeal)
        self.ideal.TESTMODE = True

    def test_connection(self):
        """Check the Mollie connection by retrieving list of banks."""
        banks = self.ideal.get_banks()
        self.assertTrue(('9999', 'TBM Bank') in banks)
