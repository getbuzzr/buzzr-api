import enum
import json


class UserErrorMessageEnum(str, enum.Enum):
    ALREADY_REFFERED = "ALREADY_REFFERED"


class AddressErrorMessageEnum(str, enum.Enum):
    NO_ADDRESS_FOUND = "NO_ADDRESS_FOUND"
    USER_HAS_NO_ADDRESS = "USER_HAS_NO_ADDRESS"
    DEFAULT_NOT_SERVICEABLE = "DEFAULT_NOT_SERVICEABLE"


class OrderErrorMessageEnum(str, enum.Enum):
    ITEM_OUT_OF_STOCK = "ITEM_OUT_OF_STOCK"
    ACTIVE_CHECKOUT_PRESENT = "ACTIVE_CHECKOUT_PRESENT"
    ADDRESS_LAT_LNG_NOT_PRESENT = "ADDRESS_LAT_LNG_NOT_PRESENT"
    NO_COST_CALCULATED = "NO_COST_CALCULATED"
    ADDRESS_DOESNT_EXIST = "ADDRESS_DOESNT_EXIST"
    NO_FEEDBACK_ALLOWED = "NO_FEEDBACK_ALLOWED"
    PHONE_NOT_VERIFIED = "PHONE_NOT_VERIFIED"
    ADDRESS_NOT_SERVICEABLE = "ADDRESS_NOT_SERVICABLE"
    STORE_NOT_OPEN = "STORE_NOT_OPEN"
    MAX_ORDERS_REACHED = "MAX_ORDERS_REACHED"
    NO_CREDIT_ORDER_FOUND = "NO_CREDIT_ORDER_FOUND"
    COST_LESS_THEN_THRESHOLD = "COST_LESS_THEN_THRESHOLD"


class PromoCodeErrorMessage(str, enum.Enum):
    PROMO_NOT_VALID = "PROMO_NOT_VALID"
    PROMO_ALREADY_REDEEMED = "PROMO_ALREADY_REDEEMED"
    NOT_FIRST_ORDER="NOT_FIRST_ORDER"


class CouponErrorMessage(str, enum.Enum):
    NO_COUPON_FOUND = "NO_COUPON_FOUND"
    DATE_NOT_VALID = "DATE_NOT_VALID"
    COUPON_ALREADY_REDEEMED = "COUPON_ALREADY_REDEEMED"


class CustomErrorMessage():

    def __init__(self, err_code, error_message="", error_detail=""):
        # set up ses client
        self.err_code = err_code
        self.error_message = error_message
        self.error_detail = error_detail

    def jsonify(self):
        """Returns a json representation of the error code

        Returns:
            [str]: {"err_code","error_message","error_detail"}
        """
        error_detail = {"err_code": self.err_code.value,
                        "error_message": self.error_message, "error_detail": self.error_detail}
        return error_detail
