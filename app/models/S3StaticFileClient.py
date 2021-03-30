import boto3
import os
import logging
from fastapi.exceptions import HTTPException


class S3StaticFileClient():
    """Model that handles connection with s3 bucket that hosts static files
    """
    PRESIGNED_EXPIRATION = 3600
    STATIC_S3_BUCKET_NAME = os.environ["STATIC_S3_BUCKET_NAME"]

    def __init__(self):
        self.s3_client = boto3.client('s3')

    def generate_profile_picture_signed_url(self, user_id, file_name):
        """Generate the signed url for user to use to upload profile picture

        Args:
            user_id (int):The id of the user
        """
        try:
            upload_data = self.s3_client.generate_presigned_post(
                Bucket=self.STATIC_S3_BUCKET_NAME,
                Key=f"users/{user_id}/{file_name}",
                Fields={
                    'acl': 'public-read'
                })
            return {
                'url': upload_data['url'],
                'key': upload_data['fields']['key'],
                'acl': upload_data['fields']['acl'],
                'AWSAccessKeyId': upload_data['fields']['AWSAccessKeyId'],
                'x-amz-security-token': upload_data['fields']['x-amz-security-token'],
                'policy': upload_data['fields']['policy'],
                'signature': upload_data['fields']['signature'],
            }
        except Exception as e:
            logging.error(f"Failed to generate presigned url: {e}")
            raise HTTPException(500)
