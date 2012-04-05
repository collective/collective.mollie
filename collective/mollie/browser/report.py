from zope.event import notify
from zope.publisher.browser import BrowserView

from collective.mollie.events import MollieIdealPaymentEvent
from collective.mollie.interfaces import IMollieIdealPayment


class ReportPaymentStatusView(BrowserView):
    """View that can be used to direct by Mollie to report the status
    of a payment.
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
