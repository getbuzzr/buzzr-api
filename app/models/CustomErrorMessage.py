import enum
import json


class CustomErrorMessageEnum(str, enum.Enum):
    NO_ADDRESS_FOUND = "NO_ADDRESS_FOUND"
    USER_HAS_NO_ADDRESS = "USER_HAS_NO_ADDRESS"


class CustomErrorMessage():

    def __init__(self, err_code: CustomErrorMessageEnum, err_message: str, err_detail: str):
        # set up ses client
        self.err_code = err_code
        self.err_message = err_message
        self.err_detail = err_detail

    def jsonify(self):
        """Returns a json representation of the error code

        Returns:
            [str]: {"err_code","err_message","err_detail"}
        """
        err_detail = {"err_code": self.err_code.value,
                      "err_message": self.err_message, "err_detail": self.err_detail}
        return json.dumps(err_detail)
