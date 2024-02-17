import base64
import logging
import requests

logger = logging.getLogger(__name__)


class ChatService:
    CHAT_ENDPOINT = 'https://api.divar.ir/v2/open-platform/chat/conversation'
    REGISTER_HOOK_ENDPOINT = 'https://api.divar.ir/v1/open-platform/notify/chat/post-conversations'

    def __init__(self, x_api_key, access_token) -> None:
        self._x_api_key = x_api_key
        self._access_token = access_token


    def register_chat_hook(self, post_token, divar_token, hook_endpoint):
        headers = {
            'x-api-key': self._x_api_key,
            'x-access-token': self._access_token,
            'content-type': 'application/json',      
        }
        json_data = {
            "post_token": post_token,
            "identification_key": divar_token,
            "endpoint": hook_endpoint
        }

        res = requests.post(self.REGISTER_HOOK_ENDPOINT, headers=headers, json=json_data)

        logger.info("message has been send to divar.")
        logger.info(res.json())
        logger.info(res.status_code)

        return res.json()

    def send_link(self, user_id, post_token, peer_id, message, btn_caption, rate_link):
        headers = {
            'x-api-key': self._x_api_key,
            'x-access-token': self._access_token,
            'content-type': 'application/json',      
        }
        json_data = {
            "user_id": user_id,
            "post_token": post_token, 
            "peer_id": peer_id,
            "type": "TEXT",
            "message": message,
            "receiver_btn": {
                "action": "DIRECT_LINK",
                "data": {
                    "icon_name": "لغو",
                    "extra_data": {
                    },
                    "direct_link": rate_link,
                    "caption": btn_caption
                }
            }
        }

        res = requests.post(self.CHAT_ENDPOINT, headers=headers, json=json_data)
        
        logger.info("message has been send to divar.")
        logger.info(res.json())
        logger.info(res.status_code)

        return res.json()
        

    def send_direct_link(self, user_id, post_token, peer_id, message):
        pass