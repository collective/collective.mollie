from zope.interface import implements

from collective.mollie.interfaces import IMollieIdeal


class MollieIdeal(object):
    implements(IMollieIdeal)
