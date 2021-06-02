from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.Address import Address, AddressStatusEnum
from models.User import User
from models.CustomErrorMessage import CustomErrorMessage, AddressErrorMessageEnum
# Schemas
from schemas.AddressSchema import AddressSchemaIn, AddressSchemaOut, AddressSchemaPut
# Auth
from auth import get_current_user
from utils import serialize
# utils
from database import get_db
import requests
import os
import json
import urllib.parse
router = APIRouter()


MAX_TIME_SECONDS = 420


@router.get('/location_is_serviceable')
def location_is_serviceable(latitude: float, longitude: float, current_user: User = Depends(get_current_user)):
    seconds_away_from_hq = get_seconds_away_from_hq(latitude, longitude)
    if seconds_away_from_hq < MAX_TIME_SECONDS:
        return {"is_serviceable": True}
    else:
        return {"is_serviceable": False}


def get_seconds_away_from_hq(latitude, longitude):
    """Checks with google maps to see if this address is valid.If it is, return seconds

    Args:
        new_address ([Address]): Address to check
    """
    COMPANY_ADDRESS_LATITUDE = 49.276567
    COMPANY_ADDRESS_LONGITUDE = -123.119116
    GOOGLE_MAPS_API_KEY = os.environ['GOOGLE_MAPS_API_KEY']
    try:
        google_maps_request = requests.get(
            f'https://maps.googleapis.com/maps/api/directions/json?origin={COMPANY_ADDRESS_LATITUDE},{COMPANY_ADDRESS_LONGITUDE}&destination={latitude},{longitude}&key={GOOGLE_MAPS_API_KEY}&mode=bicycling').json()
    except Exception as e:
        logging.error(
            f"Google server error: Request:{google_maps_request} Error: {e}")
    try:
        time_seconds = google_maps_request[
            'routes'][0]['legs'][0]['duration']['value']
    except:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE,
                            "lat/lng not a valid location")

    return time_seconds


def generate_google_maps_share_url(address):
    address_string = urllib.parse.quote_plus(
        f"{address.street_address},{address.city},{address.province},{address.country},{address.postal_code}")
    return f"http://google.com/maps/dir/?api=1&destination={address_string}&travelmode=bicycling"


def calculate_address_delivery_fee(address_id):
    return 399


def check_address_exists(address, list_of_created_addresses):
    """Check to see if the address already exists

    Args:
        address ([Address]):The address to check
        list_of_created_addresses (List[Address]): List of adddress to check for

    Returns:
        [Boolean] 
    """
    for address_created in list_of_created_addresses:
        # check street address and apartment number
        if address.street_address == address_created.street_address and address.apartment_number == address_created.apartment_number:
            return True
    return False


@router.get('/{address_id}/delivery_charge')
def get_addresses_delivery_fee(address_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    return calculate_address_delivery_fee(address_id)


@router.get('', response_model=List[AddressSchemaOut])
def get_addresses(current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    addresses = session.query(Address).filter_by(
        user_id=current_user.id, status=AddressStatusEnum.active).order_by(Address.date_created.desc()).all()
    return [serialize(x) for x in addresses]


@router.delete('/{address_id}')
def delete_address(address_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    addresses = session.query(Address).filter_by(
        user_id=current_user.id).order_by(Address.date_created.desc()).all()
    if len(addresses) == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, CustomErrorMessage(
            AddressErrorMessageEnum.USER_HAS_NO_ADDRESS, error_message="User has no address saved").jsonify())
    # get targeted address
    try:
        targeted_address = [x for x in addresses if x.id == address_id][0]
    except:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, CustomErrorMessage(
            AddressErrorMessageEnum.NO_ADDRESS_FOUND, error_message="Address with that id doesnt exist for this user").jsonify())
    # address is a default address, so set another one as default
    if targeted_address.is_default:
        # check to see if user has another address
        addresses.remove(targeted_address)
        if len(addresses) > 0:
            new_default = addresses[0]
            new_default.is_default = True
    targeted_address.status = AddressStatusEnum.deleted
    session.commit()
    return status.HTTP_200_OK


@router.post('', response_model=AddressSchemaOut)
def post_addresses(post_address: AddressSchemaIn, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    # check to see if the name already exists
    user_addresses = session.query(Address).filter_by(
        user_id=current_user.id).all()
    # create new address
    new_address = Address(name=post_address.name, user_id=current_user.id, street_address=post_address.street_address, apartment_number=post_address.apartment_number, buzzer=post_address.buzzer, postal_code=post_address.postal_code,
                          province=post_address.province, city=post_address.city, country=post_address.country, additional_instructions=post_address.additional_instructions, delivery_preference=post_address.delivery_preference, latitude=post_address.latitude, longitude=post_address.longitude)
    if post_address.name in [x.name for x in user_addresses]:
        raise HTTPException(status.HTTP_409_CONFLICT,
                            "This name is already taken")
    # check to see if the address already exists
    if check_address_exists(new_address, user_addresses):
        raise HTTPException(status.HTTP_409_CONFLICT,
                            "This address already exists")
    new_address.google_share_url = generate_google_maps_share_url(new_address)
    seconds_away_from_hq = get_seconds_away_from_hq(
        new_address.latitude, new_address.longitude)
    new_address.seconds_away_from_hq = seconds_away_from_hq
    if seconds_away_from_hq < MAX_TIME_SECONDS:
        new_address.is_serviceable = True
    else:
        new_address.is_servicable = False
        # check to make sure that the new address is not set as default
        if post_address.is_default:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, CustomErrorMessage(
                AddressErrorMessageEnum.DEFAULT_NOT_SERVICEABLE, error_message="A non serviceable address cannot be set as default").jsonify())
    # check to see if default address already exists
    try:
        default_address = [x for x in user_addresses if x.is_default][0]
    except:
        default_address = None
    # check to see if we can set user as default
    if post_address.is_default:
        # address that is default already exists so remove existing default
        if default_address:
            default_address.is_default = False
            session.add(default_address)
        new_address.is_default = True
    else:
        # if there is a no default address currently set, make sure the address is
        # serviceable before making it default
        if default_address is None and new_address.is_serviceable == True:
            new_address.is_default = True
        else:
            new_address.is_default = False
    session.add(new_address)
    session.commit()
    return serialize(new_address)


@router.put("/{address_id}", response_model=AddressSchemaOut)
def put_address(address_put: AddressSchemaPut, address_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_db)):
    # if you change location, you must add lat/lng
    if (address_put.street_address or address_put.city or address_put.country) is not None and None in (address_put.latitude, address_put.longitude):
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "if you change the location, you must add lat/lng")
    address_to_edit = session.query(Address).get(address_id)
    if address_to_edit is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            "Address doesnt exist ")
    if address_to_edit.user_id != current_user.id and not current_user.is_admin():
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            "You cant edit this address")
    # address is being set as default
    if address_put.is_default:
        # if there is already an address that is set as default, we need to remove it
        current_default_address = session.query(Address).filter_by(
            user_id=current_user.id, is_default=True).first()
        if current_default_address:
            current_default_address.is_default = False
            session.add(current_default_address)

    for key, value in address_put.dict().items():
        # If key is being edited
        if value is not None:
            setattr(address_to_edit, key, value)
    #  If user has changed location, we must update google share url/ is_servicable
    if address_put.latitude:
        seconds_away_from_hq = get_seconds_away_from_hq(
            address_put.latitude, address_put.longitude)
        address_to_edit.seconds_away_from_hq = seconds_away_from_hq
        if seconds_away_from_hq < MAX_TIME_SECONDS:
            address_to_edit.is_serviceable = True
        else:
            address_to_edit.is_servicable = False
        address_to_edit.google_share_url = generate_google_maps_share_url(
            address_put)
    session.commit()
    return serialize(address_to_edit)
