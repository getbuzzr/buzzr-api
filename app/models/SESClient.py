import boto3
import os
from datetime import datetime
import logging
import requests
from fastapi.exceptions import HTTPException
from utils import APP_ROOT


class SESClient():
    """This is the model that interacts with the SES client 
    """
    FROM_EMAIL = "hello@getbuzzr.co"

    def __init__(self):
        # set up ses client
        self.ses_client = boto3.client('ses')

    def send_invitation_email(self, first_name, last_name, email, is_dispatcher):
        """Send invitation email to user including location to create a new account

        Args:
            first_name (str): first name of the user
            last_name (str): last name of the user
            email (str): email of the user
            is_dispatcher (bool): boolean if user is dispatcher 
        """
        # gather the template
        if is_dispatcher:
            template_path = "email_templates/invite_admin_dispatcher.html"
        else:
            template_path = "email_templates/invite_user.html"
        email_template_path = os.path.join(
            APP_ROOT, template_path)
        email_template_text = open(email_template_path, "r").read()
        # replace template with placeholders
        email_template_text = email_template_text.replace("{first_name}", first_name).replace(
            "{last_name}", last_name)
        try:
            self.ses_client.send_email(Source=self.FROM_EMAIL,
                                       Destination={
                                           'ToAddresses': [email]},
                                       Message={'Subject': {'Data': "You have been invited to Onguard"},
                                                'Body': {'Html': {
                                                    'Data': email_template_text
                                                }}})
        except Exception as e:
            logging.error(e)
            raise HTTPException(500)
