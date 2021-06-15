from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.User import User, coupons_redeemed
from models.Coupon import Coupon
from models.CustomErrorMessage import CouponErrorMessage, CustomErrorMessage
#  schemas
from schemas.CouponSchema import CouponSchemaOut, CouponSchemaIn
# Auth
from auth import get_current_user_sub
from utils import serialize, get_current_user
# utils
from database import session_scope
import datetime
router = APIRouter()


@router.get('', response_model=List[CouponSchemaOut])
def get_coupons_used(current_user_sub: User = Depends(get_current_user_sub)):
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
        redeemed_coupons = session.query(coupons_redeemed).filter_by(
            user_id=current_user.id).all()
        coupons_redeemed_return = []
        for redeemed_coupon in redeemed_coupons:
            coupon = session.query(Coupon).get(redeemed_coupon.coupon_id)
            coupons_redeemed_return.append({
                "id": coupon.id,
                "coupon_code": coupon.coupon_code,
                "valid_from": coupon.valid_from,
                "credit": coupon.credit,
                "valid_until": coupon.valid_until,
                "date_redeemed": redeemed_coupon.date_redeemed
            })

        return coupons_redeemed_return


@router.post('')
def post_coupons(coupon_in: CouponSchemaIn, current_user_sub: User = Depends(get_current_user_sub)):
    with session_scope() as session:
        current_user = get_current_user(current_user_sub, session)
        coupon_targeted = session.query(Coupon).filter_by(
            coupon_code=coupon_in.coupon_code).first()
        # no coupon is found
        if coupon_targeted is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                CustomErrorMessage(
                                    CouponErrorMessage.NO_COUPON_FOUND, error_message="This coupon code doesnt exist").jsonify())
        current_datetime = datetime.datetime.utcnow()
        # check to see if date is valid
        if current_datetime < coupon_targeted.valid_from or coupon_targeted.valid_until < current_datetime:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                CustomErrorMessage(
                                    CouponErrorMessage.DATE_NOT_VALID, error_message="This coupon is not yet valid or not valid anymore").jsonify())
        # check to see if coupon has already been redeemed
        if coupon_targeted in current_user.coupons_redeemed:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                CustomErrorMessage(
                                    CouponErrorMessage.COUPON_ALREADY_REDEEMED, error_message="Coupon already redeemed").jsonify())
        current_user.coupons_redeemed.append(coupon_targeted)
        current_user.credit += coupon_targeted.credit
        session.add(current_user)
        session.commit()
        return status.HTTP_200_OK
