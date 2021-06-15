
import json
import boto3
import logging

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import session_scope
from models.User import User
from models.Rider import Rider
from functools import wraps
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def has_user_read_update_perms(func):
    """Decorator to check to see if current user has ability to read or update targeted user
    Args:
        current_user (User): current user in session
        session (Session): current db session
        user_id (int) id of targeted user
    """
    @wraps(func)
    def inner(*args, **kwargs):
        queried_user = kwargs['session'].query(User).get(kwargs['user_id'])
        if queried_user is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "User not found")
        #  allow query if user in admin org, or if their user ids match
        if (kwargs['current_user'].is_admin() and queried_user.organization_id == kwargs['current_user'].organization_id) or kwargs['current_user'].id == kwargs['user_id']:
            return func(*args, **kwargs)
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN)
    return inner


def is_admin(func):
    """Decorator to Checks to see if user is admin
    Args:
        current_user (User): current user in session
    """
    @wraps(func)
    def inner(*args, **kwargs):
        if not kwargs['current_user'].is_admin():
            raise HTTPException(
                403, "You must be an admin to use this function")
        return func(*args, **kwargs)
    return inner


def auth_user(access_token):
    """This function is used to auth user

    Args:
        access_token (str): This is the access token
    """
    cognito_client = boto3.client('cognito-idp')
    try:
        user = cognito_client.get_user(AccessToken=access_token)
    # user not authoirized by cognito
    except cognito_client.exceptions.NotAuthorizedException as e:
        raise HTTPException(401)
    except Exception as e:
        logging.error(f"Cognito couldnt auth user: {e}")
        raise HTTPException(500)

    return user


def get_current_user_sub(token: str = Depends(oauth2_scheme)):
    # try and authenticate user with access token
    user = auth_user(token)
    if user is None:
        raise HTTPException(401)
    try:
        cognito_sub = [x['Value']
                       for x in user['UserAttributes'] if x['Name'] == 'sub'][0]
    except Exception as e:
        logging.error(f"Couldnt get user {e}")
        raise HTTPException(500)
    if user is None:
        logging.info(f"Couldnt get user with sub {cognito_sub}")
        raise HTTPException(401, "No user found")
    return cognito_sub


def get_current_rider(token: str = Depends(oauth2_scheme)):
    # try and authenticate user with access token
    with session_scope() as session:
        user = auth_user(token)
        if user is None:
            raise HTTPException(401)
        try:
            cognito_sub = [x['Value']
                           for x in user['UserAttributes'] if x['Name'] == 'sub'][0]
            user = session.query(Rider).filter_by(
                cognito_sub=cognito_sub).first()
        except Exception as e:
            logging.error(f"Couldnt get rider {e}")
            raise HTTPException(500)
        if user is None:
            logging.info(f"Couldnt get rider with sub {cognito_sub}")
            raise HTTPException(401, "No rider found")
        return user
