

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

    def get_saved_payment_info(self, stripe_customer_id):
        """Get all the payment information related to the customer

        Args:
            stripe_customer_id (string): stripe customer id
        """
        try:
            payment_methods = self.stripe.PaymentMethod.list(
                customer=stripe_customer_id,
                type="card"
            )
        except Exception as e:
            logging.error(e)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
        return payment_methods.data

    def generate_ephemeral_key(self, stripe_customer_id):
        """Generate ephemeral key which allows client access to customer data on Stripe

        Args:
            stripe_customer_id ([str]): This customer id of stripe user
        """
        try:
            ephemeral_key = self.stripe.EphemeralKey.create(
                customer=stripe_customer_id,
                stripe_version='2020-08-27'
            )
        except Exception as e:
            logging.error(e)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
        return ephemeral_key

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
                amount=amount,
                currency=self.currency,
                customer=stripe_customer_id,
                payment_method_types=["card"],
            )
        except Exception as e:
            logging.error(e)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
        return payment_intent

    def edit_payment_intent(self, payment_intent_id, amount):
        """This function is used to edit a payment intent

        Args:
            payment_intent_id (str) This is the id of the payment intent
            amount (float): This is the new amount
        @returns 
            payment_intent_secret (str) New payment intent secret
        """
        try:
            payment_intent = self.stripe.PaymentIntent.modify(
                payment_intent_id,
                amount=amount,
            )
        except Exception as e:
            logging.error(e)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
        return payment_intent.client_secret
