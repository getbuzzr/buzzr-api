

from fastapi import status
import boto3
import os
import logging
from fastapi.exceptions import HTTPException
import stripe

STRIPE_SECRET = os.environ["STRIPE_SECRET_KEY"]


class StripeApiClient():
    """Model that handles connection with s3 bucket that hosts static files
    """

    def __init__(self, currency):
        self.currency = currency
        self.stripe = stripe
        self.stripe.api_key = STRIPE_SECRET

    def generate_payment_intent(self, stripe_customer_id, amount):
        """Generate stripe payment intent to charge card

        Args:
            stripe_customer_id (str): Stripe customer id
            amount (float): amount in dollar

        Raises:
            HTTPException: stripe exception
        """
        try:
            payment_intent = self.stripe.PaymentIntent.create(
                amount=int(amount*100),
                currency=self.currency,
                customer=stripe_customer_id,
                payment_method_types=["card"],
            )
        except Exception as e:
            logging.error(e)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
        return payment_intent
