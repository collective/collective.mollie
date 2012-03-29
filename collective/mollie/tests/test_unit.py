from mock import MagicMock
import unittest2 as unittest

from zope.component import getUtility

from collective.mollie.testing import COLLECTIVE_MOLLIE_INTEGRATION_TESTING
from collective.mollie.testing import do_mollie_request_side_effect
from collective.mollie.interfaces import IMollieIdeal


class TestIdealWrapper(unittest.TestCase):
    """Unit test the iDeal wrapper without connecting to Mollie."""

    layer = COLLECTIVE_MOLLIE_INTEGRATION_TESTING

    def setUp(self):
        self.ideal = getUtility(IMollieIdeal)
        self.ideal.old_do_request = self.ideal._do_request
        self.ideal._do_request = MagicMock(
            side_effect=do_mollie_request_side_effect)

    def tearDown(self):
        self.ideal._do_request = self.ideal.old_do_request

    def test_banklist(self):
        """Check the list of banks."""
        banks = self.ideal.get_banks()
        # Make sure we are sending the right parameters.
        self.ideal._do_request.assert_called_with({'a': 'banklist'}, False)
        # Make sure the result is parsed properly
        self.assertTrue(('0021', 'Rabobank') in banks)
