
import requests
import logging

logger = logging.getLogger(__name__)


class PhoneService:
    USER_ENDPOINT = 'https://api.divar.ir/v1/open-platform/users'

    def __init__(self, x_api_key, access_token) -> None:
        self._x_api_key = x_api_key
        self._access_token = access_token


    def show_phone(self):
        headers = {
            'x-api-key': self._x_api_key,
            'x-access-token': self._access_token,
            'content-type': 'application/json',      
        }

        res = requests.post(self.USER_ENDPOINT, headers=headers)

        logger.info(res.status_code)
        logger.info(res.json())

        return res.json()