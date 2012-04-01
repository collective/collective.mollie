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


More information
================

For details about the Mollie ideal API, see its documentation_.

.. _documentation: http://www.mollie.nl/support/documentatie/betaaldiensten/ideal/


Thanks
======

This package is inspired by nfg.ideal_

.. _nfg.ideal: http://pypi.python.org/pypi/nfg.ideal
