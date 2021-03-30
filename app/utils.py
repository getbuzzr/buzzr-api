from dynamodb_json import json_util as dynamo_json_util
import json
import boto3
from fastapi import FastAPI, HTTPException, Depends, status
import logging
from datetime import datetime
import os
from functools import wraps

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


def validate_id_querystring(func):
    """Decorator to validate id querystring parameter. User must be an admin to use querystring, and queried ids length
    must be less then 30
    Args:
        current_user (User): current user in session
        session (Session): current db session
        id (str) list of query params
    """
    @wraps(func)
    def inner(*args, **kwargs):
        queried_ids = kwargs['ids']
        # no queried id. Just return
        if queried_ids is None:
            return func(*args, **kwargs)

        # only admins can query ids
        if queried_ids and not kwargs['current_user'].is_admin():
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "Only admins can use id query param")
        try:
            queried_ids = queried_ids.split(',')
        except:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                "Please enter a valid 'id' query parameter seperated by a comma")

        if len(queried_ids) > 30:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "You can only query a max of 30 ids")
        return func(*args, **kwargs)
    return inner


def convert_dict_to_dynamo_item(value):
    """converts a dict to dynamo item to write to dynamo

    Args:
        value ([dict]): The dict to convert to dynamo item

    Returns:
        [dict]: dict that can be loaded into dynamo client
    """
    return json.loads(dynamo_json_util.dumps(value))


def convert_dynamo_item_to_dict(value):
    """Converts a dynamo item to a dict

    Args:
        value (dict): The dict returned by dynamo

    Returns:
        [dict]: normal dict without dynamo mapping
    """
    return dynamo_json_util.loads(value)


def get_parameter_from_ssm(path):
    client = boto3.client('ssm', region_name="us-east-1")
    try:
        parameter_value = client.get_parameter(
            Name=path,
            WithDecryption=True)['Parameter']['Value']
        return parameter_value
    except Exception as e:
        return None


def serialize(model):
    """Used to serialize models. Changes datetime to ISO-8601 format

    Args:
        model ([class]): Class model

    Returns:
        [dict]: serialized model
    """
    serialized_data = {}
    for column in model.__table__.columns:
        column_value = getattr(model, column.name)
        # serialize datetime to ISO-8601 format
        if isinstance(column_value, datetime):
            column_value = column_value.isoformat()+'Z'
        serialized_data[column.name] = column_value
    return serialized_data