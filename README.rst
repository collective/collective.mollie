Introduction
============

``collective.mollie`` provides a wrapper for the `Mollie iDeal
API`_. This wrapper *can* be used without any further Plone
integration. However, this package also provides:

 - `Adapters`_ to store payment information on objects.
 - `Browser views`_ which can be used to have Mollie report back.
 - An `event`_ which can be subscribed to to be notified when payment status has been updated.

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

Since the list of banks may change, you always need to retrieve it
before you do the payment::

    >>> from zope.component import getUtility
    >>> from collective.mollie.interfaces import IMollieIdeal
    >>> ideal_wrapper = getUtility(IMollieIdeal)
    >>> ideal_wrapper.get_banks()
    [('0031', 'ABN AMRO'), ...]

If the ``TESTMODE`` flag is set, you can retrieve a test bank::

    >>> ideal_wrapper.TESTMODE = True
    >>> ideal_wrapper.get_banks()
    [('9999', 'TBM Bank')]
    >>> ideal_wrapper.TESTMODE = False
    >>> ideal_wrapper.get_banks()
    [('0031', 'ABN AMRO'), ...]

The result of the call is a list of tuples. Each tuple consists of a
bank ID and name. The name can be used to present to the customer so
he/she can choose which bank to use. The ID is needed in the next
step.

.. note ::

   If you want to use the test mode from Molllie to test payments,
   please **also** switch your Mollie account to test mode otherwise
   Mollie will not accept a test payment, even though the URL might
   point to the test bank.


Request a payment
-----------------

When you know which bank will be used to pay, you can request a
payment with the API::

   >>> ideal_wrapper.request_payment(partner_id='999999',
   ...     bank_id='9999', amount='123', message='The message',
   ...     report_url='http://example.com/report',
   ...     return_url='http://example.com/return',
   ...     profile_key='999999')
   ('123...123', 'http://...')

The result is a ``transaction_id``, and a URL to send the customer to
to perform the payment.

.. note::

   The ``amount`` of the payment has to be in **cents**. The
   ``message`` may only be 29 characters (any more characters are
   ignored). The ``profile_key`` parameter is optional. You only need
   to use it if you want to use a different payment profile than the
   default for the specified account.


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
     'paid': True,
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

Adapters
--------

However, you can also use one of the adapters defined in the package:
``MollieIdealPayment`` and ``MollieIdealMultiplePayments``. By using
one of these, information about payments is persistently stored on the
adapted objects.

You can adapt any object that implements the ``IAttributeAnnotatable``
interface. For instance::

    >>> from zope.annotation import IAttributeAnnotatable
    >>> from persistent import Persistent
    >>> from zope.interface import Interface
    >>> class IFoo(Interface):
    >>>     pass
    >>> class Foo(Persistent):
    ...     implements(IFoo, IAttributeAnnotatable)

If you only want to store a single payment on an object, as is common
for a specific purchase, you can use the ``IMollieIdealPayment``
interface::

    >>> from collective.mollie.interfaces import IMollieIdealPayment
    >>> purchase = Foo()
    >>> purchase_payment = IMollieIdealPayment(purchase)

Now you can request banks, a payment URL and the payment status::

    >>> purchase_payment.get_banks()
    [('0031', 'ABN AMRO'), ...]
    >>> purchase_payment.get_payment_url(partner_id='999999',
    ...     bank_id='9999', amount='123', message='The message',
    ...     report_url='http://example.com/report',
    ...     return_url='http://example.com/return',
    ...     profile_key='999999')
    'http://....'
    >>> purchase_payment.get_payment_status()
    'Success'

Note that you do not have to repeat the ``partner_id`` or
``transaction_id`` when requesting the payment status. This
information was stored when you requested the payment url and is reused
for the ``get_payment_status`` call.

As stated earlier, the payment information is stored persistently::

    >>> purchase_payment.paid
    True
    >>> purchase_payment.amount
    '123'
    >>> purchase_payment.consumer
    {'name': 'T. TEST',
     'account': '0123456789',
     'city': 'Testdorp'
     }

In cases where multiple payments need to be stored on a single object,
you can use the ``IMollieIdealMultiplePayments`` interface. For
example if you want to allow multiple people to be able to donate to
some charity::

    >>> from collective.mollie.interfaces import IMollieIdealMultiplePayments
    >>> charity = Foo()
    >>> charity_donations = IMollieIdealMultiplePayments(charity)

As was previously the case, you can also request the available banks::

    >>> charity_payment.get_banks()
    [('0031', 'ABN AMRO'), ...]

When you retrieve a payment URL, you also get a transaction ID::

    >>> charity_payment.get_payment_url(partner_id='999999',
    ...     bank_id='9999', amount='123', message='The message',
    ...     report_url='http://example.com/report',
    ...     return_url='http://example.com/return',
    ...     profile_key='999999')
    ('123...', 'http://....')

This transaction ID is required when you want to access the data for a
payment::

    >>> charity_payment.get_payment_status('123...')
    'Success'
    >>> payment = charity_payment.get_transaction('123...')
    >>> payment['paid']
    True
    >>> payment['amount']
    '123'
    >>> payment['consumer']
    {'name': 'T. TEST',
     'account': '0123456789',
     'city': 'Testdorp'
     }

Note that the way to get to the payment information is also a bit
different than in the single payment case.


Browser Views
-------------

As described in the section `Check the payment`_, you have to wait with
checking the payment status until Mollie has pinged the
``report_url``.

You can write your own view, but you can also use one provided by
``collective.mollie``: the ``ReportPaymentStatusView`` and
``ReportMultiplePaymentsStatusView`` classes. These views checks
whether the ``transaction_id`` from the request matches one stored
on the object. If it does, the payment status of the object is checked
immediately.

To use the simple payment view, first register it::

    <browser:page
        for="*"
        class="collective.mollie.browser.report.ReportPaymentStatusView"
        name="report_payment_status"
        permission="zope2.View"
        />

Alternatively you can use the multiple payment report view::

    <browser:page
        for="*"
        class="collective.mollie.browser.report.ReportMultiplePaymentsStatusView"
        name="report_payment_status"
        permission="zope2.View"
        />

(You probably should only register the view for specific
interfaces. And obviously you can give it any name you want.)

Then use ``<object>/absolute_url/@@report_payment_status`` as the
``report_url`` when requesting the payment URL.


Event
-----

The report views also emit an event: ``MollieIdealPaymentEvent``. So
by implementing a subscriber in your own package, you can get a
notification if the payment information of an object is updated and
for instance change the workflow state of the object to "paid".

You can, for example, register a subscriber in your ``configure.zcml``::

  <subscriber
      for="IFoo
           collective.mollie.interfaces.IMollieIdealPaymentEvent"
      handler=".events.process_payment"
      />

And in ``events.py``::

    def process_payment(obj, event):
        """Process the payment information."""

Where ``obj`` is an instance of ``Foo`` and ``event`` is the
``MollieIdealPaymentEvent``.


More information
================

For details about the Mollie iDeal API, see its documentation_.

.. _documentation: http://www.mollie.nl/support/documentatie/betaaldiensten/ideal/


Credits
=======

This package is inspired by nfg.ideal_.

.. _nfg.ideal: http://pypi.python.org/pypi/nfg.ideal
