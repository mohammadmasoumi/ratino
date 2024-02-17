import json
import logging
from typing import Optional

import requests

from kenar.models.addon import Addon, StickyAddon
from kenar.models.encoder import KenarCustomEncoder
from kenar.utils.proxy import DivarHTTPProxy
from kenar.utils.errors import DivarException

logger = logging.getLogger(__name__)


class AddonsClient(DivarHTTPProxy):
    _CREATE_ADDON_ENDPOINT = 'https://api.divar.ir/v1/open-platform/add-ons/post/{token}'
    _IMAGE_UPLOAD_ENDPOINT = 'https://divar.ir/v2/image-service/open-platform/image.jpg'
    _STICKY_USER_VERIFICATION_ADDON_ENDPOINT = 'https://api.divar.ir/v1/open-platform/addons/user/{phone}'
    _DELETE_USER_ADDON_ENDPOINT = 'https://api.divar.ir/v1/open-platform/addons/user/{id}'

    def create_post_addon(self, token: str, addon: Addon, api_key: str, oauth_access_token: Optional[str] = None):
        json_data = json.dumps(addon, cls=KenarCustomEncoder)

        headers = {
            "x-api-key": api_key,
        }
        if oauth_access_token is not None:
            headers['x-access-token'] = oauth_access_token

        r: requests.Response = self._post(
            self._CREATE_ADDON_ENDPOINT.format(token=token),
            data=json_data,
            headers=headers,
            timeout=2,
        )

        if r.status_code != 200:
            logger.error("failed to create post addon", r.content, r.status_code)
            raise DivarException(message="مشکل در ساخت افزونه")

    def upload_image(self, fp) -> str:
        with open(fp, 'rb') as file:
            r: requests.Response = self._put(
                self._IMAGE_UPLOAD_ENDPOINT,
                data=file,
                headers={
                    'Content-Type': 'image/jpeg',
                },
                timeout=10,
            )

        if r.status_code != 201:
            logger.error("failed to upload image", r.content, r.status_code)
            raise DivarException("مشکل در ساخت افزونه")

        return r.json()["image_name"]

    def create_sticky_user_verification_addon(self, phone: str, sticky_addon: StickyAddon, api_key: str,
                                              oauth_access_token: str):
        json_data = json.dumps(sticky_addon, cls=KenarCustomEncoder)

        headers = {
            "x-api-key": api_key,
            'x-access-token': oauth_access_token,
        }

        r: requests.Response = self._post(
            self._STICKY_USER_VERIFICATION_ADDON_ENDPOINT.format(phone=phone),
            data=json_data,
            headers=headers,
            timeout=2,
        )

        if r.status_code != 200:
            logger.error("failed to create sticky addon", r.content, r.status_code)
            raise DivarException(message="مشکل در ساخت افزونه")
        return r.json()["id"]

    def delete_user_addon(self, user_addon_id: str, api_key: str, oauth_access_token: str):

        headers = {
            "x-api-key": api_key,
            'x-access-token': oauth_access_token,
        }

        r: requests.Response = self._delete(
            self._DELETE_USER_ADDON_ENDPOINT.format(id=user_addon_id),
            headers=headers,
            timeout=2,
        )

        if r.status_code != 200:
            logger.error("failed to delete sticky addon", r.content, r.status_code)
            raise DivarException(message="مشکل در حدف افزونه")


addons_client = AddonsClient.get_instance()
