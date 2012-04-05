from zope.interface import Interface, Attribute


class IMollieIdeal(Interface):
    """A utility that wraps the Mollie iDeal API."""

    def get_banks():
        """Return a list of bank id and name tuples.

        E.g.: [('0031, 'ABN AMRO'), ('0721', 'Postbank')]
        """

    def request_payment(partner_id, bank_id, amount, message, report_url,
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

    def check_payment(partner_id, transaction_id):
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


class IMollieIdealPayment(Interface):
    """Model to store payment information."""

    last_update = Attribute('Date/time of last change of the data.')
    transaction_id = Attribute('Transaction ID')
    amount = Attribute('Amount')
    currency = Attribute('Currency')
    paid = Attribute('Paid')
    consumer = Attribute('Consumer information')
    status = Attribute('Status')
    last_status = Attribute('Last status')

    def get_banks():
        """Return a list of bank id and name tuples.

        E.g.: [('0031, 'ABN AMRO'), ('0721', 'Postbank')]
        """

    def get_payment_url(partner_id, bank_id, amount, message,
                        report_url, return_url, profile_key=None):
        """Return the URL to redirect the customer to to do the payment.

        Also internally store the data for later reference.
        """

    def get_payment_status():
        """Retrieve and return the payment status."""


class IMollieIdealPaymentEvent(Interface):
    """An event signalling that Mollie an iDeal payment has been processed."""

    context = Attribute('The object the payment was processed for.')
    request = Attribute('The request')
