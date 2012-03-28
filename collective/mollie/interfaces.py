from zope.interface import Interface


class IMollieIdeal(Interface):
    """A utility that wraps the Mollie iDeal API."""

    def get_banks(testmode=False):
        """Return a list of bank id and name tuples.

        E.g.: [('0031, 'ABN AMRO'), ('0721', 'Postbank')]

        @testmode determines whether we get the actual list of banks
        or only the test bank 'The Big Mollie Bank'.
        """
