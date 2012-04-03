Introduction
============

``collective.mollie`` provides a wrapper for the `Mollie iDeal API`_.

.. _`Mollie iDeal API`: http://www.mollie.nl/support/documentatie/betaaldiensten/ideal/


iDeal
=====

The complete iDeal payment process contains the following steps:

1. `Request the list of banks`_
2. `Request a payment`_
3. `Have the customer do the payment`_
4. `Check the payment`_
5. `Customer is returning to the site`_


Request the list of banks
-------------------------

Since the list of banks may change, you always need to retrieve the
list of banks before you do the payment::

    >>> from zope.component import getUtility
    >>> from collective.mollie.interfaces import IMollieIdeal
    >>> ideal_wrapper = getUtility(IMollieIdeal)
    >>> ideal_wrapper.get_banks()
    [('0031', 'ABN AMRO'), ...]


Alternatively you can retrieve a test bank by adding a ``testmode`` flag::

    >>> ideal_wrapper.get_banks(testmode=True)
    [('9999', 'TBM Bank')]

The result of the call is a list of tuples. Each tuple consists of a
bank ID and name. The name can be used to present to the customer so
he/she can choose which bank to use. The ID is needed in the next
step.


Request a payment
-----------------

When you know which bank will be used to pay, you can request a
payment with the API::

   >>> ideal_wrapper.request_payment(partner_id='999999',
   ...     bank_id='9999', amount='123', message='The message',
   ...     report_url='http://example.com/report',
   ...     return_url='http://example.com/return',
   ...     profile_key='999999', testmode=False)
   ('123...123, 'http://...')

The result is a ``transaction_id``, and a URL to send the customer to
to perform the payment.

.. note::

   The ``amount`` of the payment has to be in **cents**. The
   ``message`` may only be 29 characters (any more characters are
   ignored). The ``profile_key`` parameter is optional. You only need
   to use it if you want to use a different payment profile than the
   default for the specified account.

   Again, the ``testmode`` flag is optional and defaults to False. Be
   sure to also switch your Mollie account to test mode otherwise
   Mollie will not accept a test payment, even though the URL might
   point to the test bank.


Have the customer do the payment
--------------------------------

This package does not handle this step. You should redirect the
customer to the URL returned by ``request_payment``, and hope he/she
completes the transaction.


Check the payment
-----------------

Once the ``report_url`` (see `Request a payment`_) has been pinged by
Mollie, you can check the status of the payment::

    >>> ideal_wrapper.check_payment(partner_id='999999',
    ...                             transaction_id='123...123')
    {'transaction_id': '123...123',
     'amount': '123',
     'currency': 'EUR',
     'payed': True,
     'status': 'Success',
     'consumer': {
         'name': 'T. TEST',
         'account': '0123456789',
         'city': 'Testdorp'
     }
    }

When the state is anything other than "Success", there will be no data
about the consumer.


Customer is returning to the site
---------------------------------

This is where the customer is returned to the ``return_url``. However,
this step is not handled by this package. You should use the result
from the previous step (`Check the payment`_) to inform the customer
and present further actions, where appropriate.

It may happen that the ``report_url`` is not yet called and thus the
state of the payment is not yet known. Mollie advises to report to the
customer that the status is unknown but that the payment will be
automatically processed once the status is final.


Plone integration
=================

If you want to integrate iDeal payments in your Plone project, you can
use the iDeal wrapper as defined in the ``MollieIdeal`` utility which
was described above.

Adapter
-------

However, you can also use the adapter defined in the
``MollieIdealPayment`` class. By using this adapter, information about
the payment is persistently stored on the adapted objects.

You can adapt any object that implements the ``IAttributeAnnotatable``
interface. For instance::

    >>> from zope.annotation import IAttributeAnnotatable
    >>> from persistent import Persistent
    >>> class Foo(Persistent):
    ...     implements(IAttributeAnnotatable)
    >>> foo = Foo()

This object ``foo`` can now be adapted::

    >>> from collective.mollie.interfaces import IMollieIdealPayment
    >>> foo_payment = IMollieIdealPayment(foo)

And we can request banks, a payment URL and the payment status::

    >>> foo_payment.get_banks()
    [('0031', 'ABN AMRO'), ...]
    >>> foo_payment.get_payment_url(partner_id='999999',
    ...     bank_id='9999', amount='123', message='The message',
    ...     report_url='http://example.com/report',
    ...     return_url='http://example.com/return',
    ...     profile_key='999999', testmode=False)
    'http://....'
    >>> foo_payment.get_payment_status()
    'Success'

Note that we do not have to repeat the ``partner_id`` or
``transaction_id`` when requesting the payment status. This
information was stored when we requested the payment url and is reused
for the ``get_payment_status`` call.

As stated earlier, the payment information is stored persistently::

    >>> foo_payment.payed
    True
    >>> foo_payment.amount
    '123'
    >>> foo_payment.consumer
    {'name': 'T. TEST',
     'account': '0123456789',
     'city': 'Testdorp'
     }


Report URL
----------

As described in the section `Check the payment`_, you have to wait with
checking the payment status until Mollie has pinged the
``report_url``.

You can write your own view, but you can also use the one provided by
``collective.mollie``: the ``ReportPaymentStatusView`` class. This
view checks whether the ``transaction_id`` from the request matches
the one stored on the object. If it does, the payment status of the
object is checked immediately.

To use the view, first register it::

  <browser:page
      for="*"
      class="collective.mollie.browser.report.ReportPaymentStatusView"
      name="report_payment_status"
      permission="zope2.View"
      />

(You probably should only register the view for specific
interfaces. And obviously you can give it any name you want.)

Then use ``<object>/absolute_url/@@report_payment_status`` as the
``report_url`` when requesting the payment URL.

The view also emits an event: ``MollieIdealPaymentEvent``. So by
implementing a subscriber in your own package, you can get a
notification if the payment information of an object is updated.


More information
================

For details about the Mollie iDeal API, see its documentation_.

.. _documentation: http://www.mollie.nl/support/documentatie/betaaldiensten/ideal/


Thanks
======

This package is inspired by nfg.ideal_

.. _nfg.ideal: http://pypi.python.org/pypi/nfg.ideal
