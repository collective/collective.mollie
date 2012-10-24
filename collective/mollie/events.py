from zope.interface import implements
from zope.component.interfaces import ObjectEvent

from collective.mollie.interfaces import IMollieIdealPaymentEvent


class MollieIdealPaymentEvent(ObjectEvent):
    implements(IMollieIdealPaymentEvent)

    def __init__(self, context, request, transaction_id=None):
        super(MollieIdealPaymentEvent, self).__init__(context)
        self.context = context
        self.request = request
        self.transaction_id = transaction_id
