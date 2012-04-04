from persistent.mapping import PersistentMapping

from DateTime import DateTime
from zope.annotation import IAttributeAnnotatable, IAnnotations
from zope.component import adapts
from zope.interface import implements
from zope.component import getUtility

from collective.mollie.config import IDEAL_PAYMENT_ANNOTATION_KEY
from collective.mollie.interfaces import IMollieIdeal
from collective.mollie.interfaces import IMollieIdealPayment


class MollieIdealPayment(object):
    implements(IMollieIdealPayment)
    adapts(IAttributeAnnotatable)

    def __init__(self, context):
        self.ideal_wrapper = getUtility(IMollieIdeal)
        annotations = IAnnotations(context)
        self._metadata = annotations.get(IDEAL_PAYMENT_ANNOTATION_KEY, None)
        if self._metadata is None:
            self._metadata = PersistentMapping()
            annotations[IDEAL_PAYMENT_ANNOTATION_KEY] = self._metadata

    # Properties

    def _getter(self, key):
        return self._metadata.get(key)

    def _setter(self, key, value):
        self._metadata[key] = value

    _partner_id = property(lambda self: self._getter('partner_id'),
        lambda self, value: self._setter('partner_id', value))

    _partner_id = property(lambda self: self._getter('profile_key'),
        lambda self, value: self._setter('profile_key', value))

    last_update = property(lambda self: self._getter('last_update'),
        lambda self, value: self._setter('last_update', value))

    transaction_id = property(lambda self: self._getter('transaction_id'),
        lambda self, value: self._setter('transaction_id', value))

    amount = property(lambda self: self._getter('amount'),
        lambda self, value: self._setter('amount', value))

    currency = property(lambda self: self._getter('currency'),
        lambda self, value: self._setter('currency', value))

    paid = property(lambda self: self._getter('paid'),
        lambda self, value: self._setter('paid', value))

    consumer = property(lambda self: self._getter('consumer'),
        lambda self, value: self._setter('consumer', value))

    status = property(lambda self: self._getter('status'),
        lambda self, value: self._setter('status', value))

    last_status = property(lambda self: self._getter('last_status'),
        lambda self, value: self._setter('last_status', value))

    # Methods

    def get_banks(self):
        return self.ideal_wrapper.get_banks()

    def get_payment_url(self, partner_id, bank_id, amount, message,
                        report_url, return_url, profile_key=None):
        transaction_id, url = self.ideal_wrapper.request_payment(
            partner_id, bank_id, amount, message, report_url,
            return_url, profile_key)

        self.transaction_id = transaction_id
        self._partner_id = partner_id
        self._profile_key = profile_key
        self.amount = amount
        self.last_update = DateTime()
        return url

    def get_payment_status(self):
        order_info = self.ideal_wrapper.check_payment(
            self._partner_id, self.transaction_id)
        if order_info['status'] != 'CheckedBefore':
            # Only store the main info the first time.
            self.currency = order_info['currency']
            self.paid = order_info['paid']
            self.consumer = order_info.get('consumer')
            self.status = order_info['status']
        self.last_status = order_info['status']
        self.last_update = DateTime()
        return self.last_status
