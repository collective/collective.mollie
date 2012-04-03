from zope.interface import implements

from collective.mollie.interfaces import IMollieIdealPaymentEvent


class MollieIdealPaymentEvent(object):
    implements(IMollieIdealPaymentEvent)

    def __init__(self, obj):
        self.obj = obj
