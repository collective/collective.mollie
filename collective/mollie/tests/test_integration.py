import unittest2 as unittest

from zope.component import getUtility

from collective.mollie.testing import COLLECTIVE_MOLLIE_INTEGRATION_TESTING
from collective.mollie.interfaces import IMollieIdeal


class TestIdealWrapper(unittest.TestCase):

    layer = COLLECTIVE_MOLLIE_INTEGRATION_TESTING

    def setUp(self):
        self.ideal = getUtility(IMollieIdeal)

    def test_banklist(self):
        """Check the list of banks."""
        banks = self.ideal.get_banks(testmode=True)
        self.assertTrue(('9999', 'TBM Bank') in banks)
