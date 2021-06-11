import boto3
import os
from datetime import datetime
import logging
import requests
from fastapi.exceptions import HTTPException
from utils import APP_ROOT
from fastapi import HTTPException, status


class SlackWebhookClient():
    """This is the slack webhook
    """
    DELIVERY_ENDPOINT = os.environ['SLACK_DELIVERY_WEBHOOK_ENDPOINT']

    def __init__(self):
        # set up ses client
        self.ses_client = boto3.client('ses')

    def post_delivery(self, order_id, user, user_address, items_ordered):
        """This is to post a delivery message to slack #delivery

        Args:
            user ([int]): [description]
            user_address ([str]): [description]
            items_ordered ([List[ProductOrdered] ]): [description]
            date_order_created ([datetime]): [description]
        """

        order_string = "- ".join(
            [f"*Quantity:* {x.quantity}, *Product:* {x.product.name} \n" for x in items_ordered])
        address_string = f"{user_address.street_address}"
        address_string = address_string + \
            f"\n *Preference:* {user_address.delivery_preference}"
        if user_address.buzzer:
            address_string = address_string + \
                f"\n *Buzzer:* {user_address.buzzer}"
        if user_address.apartment_number:
            address_string = address_string + \
                f"\n *Apartment Number:* {user_address.buzzer} \n"
        if user_address.additional_instructions:
            address_string = address_string + \
                f"\n *Additional Instructions:* {user_address.additional_instructions} \n"
        payload = f"{{\"text\":\"<!here> *New Order - {order_id}* \n *Name*:{user.first_name} {user.last_name} \n *Phone Number* : {user.phone_number} \n *Address Google Maps*: {user_address.google_share_url}\n*Address*: \n {address_string} *Items Ordered*\n- {order_string} \"}}"
        headers = {
            'Content-Type': "application/json",
        }
        try:
            response = requests.post(
                self.DELIVERY_ENDPOINT, data=payload, headers=headers)
        except Exception as e:
            logging.info(e)
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)
        pass
