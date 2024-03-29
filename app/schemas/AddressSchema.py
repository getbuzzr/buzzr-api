from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime

from models.Address import DeliveryPreferenceEnum


class AddressSchemaIn(BaseModel):
    """This is the address schema that the user can input
    """
    name: constr(min_length=3)
    street_address: constr(min_length=3)
    apartment_number: Optional[str]
    buzzer: Optional[str]
    postal_code: constr(min_length=3)
    province: constr(min_length=2)
    country: constr(min_length=2)
    city: constr(min_length=2)
    is_default: bool
    additional_instructions: Optional[str]
    delivery_preference: DeliveryPreferenceEnum
    latitude: float
    longitude: float


class AddressSchemaPut(BaseModel):
    """This is the address schema that the user can input
    """
    name: Optional[constr(min_length=3)]
    street_address: Optional[constr(min_length=3)]
    apartment_number: Optional[str]
    buzzer: Optional[str]
    postal_code: Optional[constr(min_length=6)]
    province: Optional[constr(min_length=2)]
    country: Optional[constr(min_length=2)]
    city: Optional[constr(min_length=2)]
    is_default: bool
    additional_instructions: Optional[str]
    delivery_preference: DeliveryPreferenceEnum
    latitude: Optional[float]
    longitude: Optional[float]


class AddressSchemaOut(BaseModel):
    """This is the address schema that the user can input
    """
    id: int
    name: str
    street_address: str
    apartment_number: Optional[str]
    buzzer: Optional[str]
    postal_code: str
    province: str
    country: str
    city: str
    is_default: bool
    additional_instructions: Optional[str]
    delivery_preference: DeliveryPreferenceEnum
    latitude: float
    longitude: float
    is_serviceable: bool
