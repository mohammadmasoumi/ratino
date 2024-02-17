import json
import logging
import requests
from rest_framework import permissions
from rest_framework.views import APIView

import divar_openplatform.settings as settings

from dataclasses import dataclass
from django.conf import settings
from django.http import HttpResponse
from django.views import View

from divar_homepage.models import Scope, DivarProfile
from misc.divar.chat import ChatService
from misc.utils.strings import gen_random_str
from misc.clients.redis import statestore_redis
from kenar.clients.finder import finder_client

logger = logging.getLogger(__name__)

SEND_MSG_URL = "https://api.divar.ir/v2/open-platform/chat/conversation"
RATE_PAGE_BASE_URL = "https://api.example.com/rate/form"


@dataclass
class ChatInfo:
    supplier: DivarProfile = None
    demand: DivarProfile = None
    post_token: str = ""


def divar_auth(func):
    def wrapper(self, request, *args, **kwargs):
        auth = request.headers['authorization']
        if auth != settings.DIVAR_TOKEN:
            return HttpResponse(status=401)

        return func(self, request, *args, **kwargs)

    return wrapper


class DivarInteractionView(View):

    @divar_auth
    def post(self, request):
        """
        Handle the POST request to the API endpoint.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The HTTP response object.

        Raises:
            None
        """
        data = json.loads(request.body)
        state = data.get('extra_data', {}).get('provider_data', {}).get('state')

        if state is None:
            # first time
            state = gen_random_str(size=10)

        statestore_redis.setex(name=state, time=60 * 60, value=json.dumps(data))

        response_data = {
            "status": "200",
            "message": "success",
            "url": f"{settings.DOMAIN}/divar/home/{state}"
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json")


class DivarChatNotifierView(APIView):
    permission_classes = [permissions.AllowAny]

    @divar_auth
    def post(self, request):
        data = json.loads(request.body)

        text = data.get("payload").get("data").get("text")
        _, is_srv_msg = self._is_service_message(text)
        chat_info = self._get_chat_info(data)
        if is_srv_msg:
            self._send_review_message(chat_info)

        logger.info("========= DIVAR CHAT NOTIFIER =========")
        logger.info(f"data: {data}")

        return HttpResponse(json.dumps(data), content_type="application/json")

    def _is_service_message(self, text: str) -> str:
        service_text_dict = {
            "sp1": "لطفا بعد از رسیدن سفیر",
            "sp2": "سفارش را برای خریدار ارسال کرده و اطلاعات مرسوله را پر کنید",
            "sp3": "بارنامه مرسوله شما صادر شد",
            "sp4": "لطفا ظرف 1 روز کاری مرسوله را تحویل نماینده پستِکس دهید.",
            "sp5": "سفارش پیک در اسنپ باکس ثبت شد، در انتظار قبول درخواست از طرف راننده هستیم.",
        }
        for service in service_text_dict:
            if service_text_dict[service] in text:
                return (service, True)
        return (None, False)

    @staticmethod
    def _create_profile(user: json, post_token: str):
        id = user["id"]
        is_supplier = user["is_supply"]
        access_token = Scope.objects.filter(post_token=post_token).first().access_token
        profile_query = DivarProfile.objects.filter(user_id=id)
        exists = profile_query.exists()
        if not exists:
            phone = ''
            if is_supplier:
                divar_user_data = finder_client.get_user(api_key=settings.DIVAR_API_KEY, access_token=access_token)
                phone = divar_user_data["phone_numbers"][0]
                logger.info("========= DIVAR CHAT NOTIFIER create_profile =========")
                logger.info(f"data: {divar_user_data}")
            return DivarProfile(user_id=id, phone = phone).save()
        else:
            return profile_query.first()

    def _get_chat_info(self, data: json):
        sender_data = data.get("payload").get("sender")
        receiver_data = data.get("payload").get("receiver")
        post_token = data.get("payload").get("metadata").get("post_token")

        sender = self._create_profile(sender_data, post_token)
        receiver = self._create_profile(receiver_data, post_token)

        if sender_data["is_supply"]:
            return ChatInfo(
                supplier=sender,
                demand=receiver,
                post_token=post_token
            )
        else:
            return ChatInfo(
                supplier=receiver,
                demand=sender,
                post_token=post_token
            )

    def _send_review_message(self, chat_info: ChatInfo):
        rate_link = f"{RATE_PAGE_BASE_URL}?" + \
                    f"supplier_id={chat_info.supplier.pk}&" + \
                    f"demand_id={chat_info.demand.pk}&" + \
                    f"post_token={chat_info.post_token}"

        access_token = Scope.objects.filter(post_token=chat_info.post_token).first().access_token
        res = ChatService(
            x_api_key=settings.DIVAR_API_KEY,
            access_token=access_token
        ).send_link(
            user_id=chat_info.supplier.user_id,
            peer_id=chat_info.demand.user_id,
            post_token=chat_info.post_token,
            message="بابت فرایند موفقی که داشتیم خوشحالم. عالی میشه اگر نظرتون رو برام ثبت کنید",
            btn_caption="ثبت نظر",
            rate_link=rate_link
        )
