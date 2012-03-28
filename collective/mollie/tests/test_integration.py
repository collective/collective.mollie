import unittest2 as unittest

from zope.component import getUtility

from collective.mollie.testing import COLLECTIVE_MOLLIE_INTEGRATION_TESTING
from collective.mollie.interfaces import IMollieIdeal


class TestIntegration(unittest.TestCase):

    layer = COLLECTIVE_MOLLIE_INTEGRATION_TESTING

    def test_utility(self):
        """Test that the utility can be found."""
        getUtility(IMollieIdeal)
