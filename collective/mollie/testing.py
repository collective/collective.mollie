from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting

from zope.configuration import xmlconfig


class CollectiveMollie(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.mollie
        xmlconfig.file('configure.zcml', collective.mollie,
                       context=configurationContext)

COLLECTIVE_MOLLIE_FIXTURE = CollectiveMollie()
COLLECTIVE_MOLLIE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_MOLLIE_FIXTURE,), name="CollectiveMollie:Integration")
