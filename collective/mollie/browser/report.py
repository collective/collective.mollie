from zope.event import notify
from zope.publisher.browser import BrowserView

from collective.mollie.adapter import UnknownTransactionError
from collective.mollie.events import MollieIdealPaymentEvent
from collective.mollie.interfaces import IMollieIdealMultiplePayments
from collective.mollie.interfaces import IMollieIdealPayment


class ReportPaymentStatusView(BrowserView):
    """View that can be used to by Mollie to report the status of a
    payment.

    This view assumes only one payment can be done on the context and
    thus uses the MollieIdealPayments adapter.
    """

    def __call__(self):
        """Return the right status code for Mollie and process the payment."""
        adapted = IMollieIdealPayment(self.context)
        received_transaction_id = self.request.form.get('transaction_id')

        if (not received_transaction_id or
            received_transaction_id != adapted.transaction_id):
            message = 'Wrong or missing transaction ID'
            self.request.response.setStatus(403, message)
            return message

        adapted.get_payment_status()
        notify(MollieIdealPaymentEvent(self.context, self.request))
        self.request.response.setStatus(200)
        return 'OK'


class ReportMultiplePaymentsStatusView(BrowserView):
    """View that can be used to by Mollie to report the status of a
    payment.

    This view assumes multiple payments can be done on the context and
    thus uses the MollieIdealMultiplePayments adapter.
    """

    def __call__(self):
        """Return the right status code for Mollie and process the payment."""
        adapted = IMollieIdealMultiplePayments(self.context)
        received_transaction_id = self.request.form.get('transaction_id')

        try:
            transaction = adapted.get_transaction(received_transaction_id)
        except UnknownTransactionError:
            transaction = None
        if (not received_transaction_id or transaction is None):
            message = 'Wrong or missing transaction ID'
            self.request.response.setStatus(403, message)
            return message

        adapted.get_payment_status(received_transaction_id)
        notify(MollieIdealPaymentEvent(self.context, self.request))
        self.request.response.setStatus(200)
        return 'OK'
