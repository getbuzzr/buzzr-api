
import json
import boto3
import logging

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models.User import User
from models.Dispatcher import Dispatcher
from models.Group import Group
from functools import wraps
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def has_group_write_perms(func, *args, **kwargs):
    """Decorator to Checks to see if user has group read permissions 
    """
    @wraps(func)
    def inner(*args, **kwargs):
        group = kwargs['session'].query(Group).get(kwargs['group_id'])
        if group is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Group not found")
        # if user is admin and in same organization or if user is in group or user is dispatcher assigned to group
        if kwargs['current_user'].is_admin() and group.organization_id == kwargs['current_user'].organization_id:
            return func(*args, **kwargs)
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "You dont have permissions to make this call")
    return inner


def has_group_read_perms(func, *args, **kwargs):
    """Decorator to Checks to see if user has group read permissions 
    """
    @wraps(func)
    def inner(*args, **kwargs):
        group = kwargs['session'].query(Group).get(kwargs['group_id'])
        if group is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Group not found")
        # if user is admin and in same organization or if user is in group or user is dispatcher assigned to group
        if (kwargs['current_user'].is_admin() and group.organization_id == kwargs['current_user'].organization_id) or group in kwargs['current_user'].groups or group in Dispatcher().get_by_user_id(kwargs['current_user'].id, kwargs['session']).groups:
            return func(*args, **kwargs)
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                "You dont have permissions to make this call")
    return inner


def has_dispatcher_read_update_perms(func):
    """Decorator to check to see if current user has ability to read or update targeted dispatcher
    Args:
        current_user (User): current user in session
        session (Session): current db session
        dispatcher_id (int) id of dispatcher
    """
    @wraps(func)
    def inner(*args, **kwargs):
        dispatcher = kwargs['session'].query(
            Dispatcher).get(kwargs['dispatcher_id'])
        if dispatcher is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                "Dispatcher not found")
        #  allow query if user in admin org, or if user id matches dispatcher user_id
        if (kwargs['current_user'].is_admin() and dispatcher.user.organization_id == kwargs['current_user'].organization_id) or dispatcher.user_id == kwargs['current_user'].id:
            return func(*args, **kwargs)
        else:
            raise HTTPException(status.HTTP_403_FORBIDDEN)
    return inner


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


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)):
    # try and authenticate user with access token
    user = auth_user(token)
    if user is None:
        raise HTTPException(401)
    try:
        cognito_sub = [x['Value']
                       for x in user['UserAttributes'] if x['Name'] == 'sub'][0]
        user = session.query(User).filter_by(
            cognito_sub=cognito_sub).first()
    except Exception as e:
        logging.error(f"Couldnt get user {e}")
        raise HTTPException(500)
    if user is None:
        logging.info(f"Couldnt get user with sub {cognito_sub}")
        raise HTTPException(401, "No user found")
    return user
