import json
import logging
import base64
from urllib.parse import urlencode

from django.views import View
from django.conf import settings
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import render, redirect

from divar_homepage.forms import ChatForm, PhoneForm
from misc.divar.chat import ChatService
from misc.divar.phone import PhoneService
from misc.divar.oauth import OAuthService
from misc.utils.strings import gen_random_str 
from misc.clients.redis import statestore_redis
from .models import DivarProfile, Scope

logger = logging.getLogger(__name__)


class ActionManager:

    def __init__(self, state) -> None:
        self.state = state
        self.data = None


    def load_data(self):
        try:
            self.data = json.loads(statestore_redis.get(self._state))
        except Exception as e:
            logger.error(e)
            self.data = None
    
    def get_access_token(self, scope):
        authorixation = self.data.get(scope)
        # todo: check expiry
        return authorixation.get('access_token')


class ChatManager(ActionManager):

    @property
    def conversation_id(self):
        encoded_scope = f"{self.data['user_id']}:{self.data['post_token']}:{self.data['peer_id']}".encode("ascii")
        base64_bytes = base64.b64encode(encoded_scope)
        return base64_bytes.decode("ascii")

    def run(self):
        self.load_data()

        if self.data is None:
            raise ValueError('data is empty')

        scope = f'CHAT_SEND_MESSAGE_OAUTH__{self.conversation_id}'
        access_token = self.get_access_token(scope) 
        if not access_token:
            pass 


class PermissionsPage(View):
    template_name = 'homepage.html'

    def get(self, request, *args, **kwargs):
        post_token = request.GET.get('post_token', None)
        scopes = f'CHAT_READ_POST_CONVERSATIONS__{post_token}+CHAT_SEND_MESSAGE_POST_CONVERSATIONS__{post_token}+USER_ADDON_CREATE+USER_PHONE'
        params = {
                    'response_type' : 'code',
                    'client_id' : settings.DIVAR_APP_SLUG,
                    'redirect_uri' : settings.DIVAR_FALLBACK_REDIRECT_URL,
                    'scope' : scopes,
                    'state' : post_token,
                }
        
        redirect_uri = settings.DIVAL_OAUTH_REDIRECT_URL + f'?{urlencode(params)}'.replace('%2B', '+')

        logger.info("============ PermissionPage ============")
        logger.info(redirect_uri)
        return redirect(redirect_uri)

    def post(self, request, *args, **kwargs):
        pass

class AccessTokenPage(View):
    template_name = 'success.html'

    def get(self, request, *args, **kwargs):
        logger.info("============= DIVAR OAUTH CALLBACK =================")

        code = request.GET.get('code', None)
        state = request.GET.get('state', None) # status -> post_token

        logger.info("code: %s", code)
        logger.info("status: %s", state)

        if code is None:
            return HttpResponse(content='application/json', status=401)

        if state is None:
            return HttpResponse(content='application/json', status=401)

        post_token = state
        exists = Scope.objects.filter(post_token=post_token).exists()
        if not exists:
            oauth_service = OAuthService(client_secret=settings.DIVAR_API_KEY, app_slug=settings.DIVAR_APP_SLUG)
            result = oauth_service.get_access_token(code=code)
            if result is None:
                logger.error(result)
                return HttpResponse(content='application/json', status=401)
        
            access_token = result.get('access_token')
            name = f'CHAT_READ_POST_CONVERSATIONS__{post_token}+CHAT_SEND_MESSAGE_POST_CONVERSATIONS__{post_token}+USER_ADDON_CREATE+USER_PHONE'

            Scope.objects.create(name=name, access_token=access_token, post_token=post_token)
            
            logger.info("name: %s", name)
            logger.info("post_token: %s", post_token)
            logger.info("access_token: %s", access_token)
            logger.info("scope has been created successfully.") 

            res = ChatService(
                x_api_key=settings.DIVAR_API_KEY, 
                access_token=access_token
            ).register_chat_hook(post_token, settings.DIVAR_TOKEN, settings.DIVAR_READ_CHAT_MESSAGE_URL)

            logger.info("============= CHAT HOOK RES =================")
            logger.info(res)


        return render(request, self.template_name)
    

class SuccessView(View):
    template_name = 'success.html'

    def get(self, request):
        logger.info("<<<<<<< Hurray, we got some users. >>>>>>>" )
        return render(request, self.template_name, content_type='application/html')


class ChatView(View):
    template_name = 'homepage.html'

    def post(self, request, *args, **kwargs):
        form = ChatForm(request.POST)
        if form.is_valid():
            state = form.cleaned_data.get('state')

            try:
                data = json.loads(statestore_redis.get(state))
            except Exception as e:
                logger.error(e)
                return render(request, self.template_name, {'chat_form': form, 'phone_form': PhoneForm(), 'error': 'Invalid state'})

            # todo: check the expiry
            conversation_id = gen_conversation_id(data.get('user_id'), data.get('post_token'), data.get('peer_id'))
            scope = f'CHAT_SEND_MESSAGE_OAUTH__{conversation_id}'
            authorization_info = data.get(scope, {})

            access_token = authorization_info.get('access_token')
            if access_token is None:
                # divar oauth fellow to get access_token
                params = {
                    'response_type' : 'code',
                    'client_id' : settings.DIVAR_APP_SLUG,
                    'redirect_uri' : settings.DIVAR_FALLBACK_REDIRECT_URL,
                    'scope' : scope,
                    'state' : f"{state}||{scope}",
                }
                redirect_uri = settings.DIVAL_OAUTH_REDIRECT_URL + f'?{urlencode(params)}'
                return redirect(redirect_uri)

            else:
                logger.info("Sending chat ....")
                chat_service = ChatService(x_api_key=settings.DIVAR_API_KEY, access_token=access_token)
                res = chat_service.send_link(data.get('user_id'), data.get('post_token'), data.get('peer_id'), form.cleaned_data.get('message'))
                
                logger.info("Sending message in chat result")
                logger.info(res)

                return render(request, self.template_name, {'chat_form': form, 'phone_form': PhoneForm()})
        else:
             render(request, self.template_name, {'chat_form': form, 'phone_form': PhoneForm()})
        

def gen_conversation_id(user_id, post_token, peer_id):
    encoded_scope = f"{user_id}:{post_token}:{peer_id}".encode("ascii")
    base64_bytes = base64.b64encode(encoded_scope)
    return base64_bytes.decode("ascii")


class PhoneView(View):
    template_name = 'homepage.html'

    def post(self, request, *args, **kwargs):
        form = PhoneForm(request.POST)
        if form.is_valid():
            state = form.cleaned_data.get('state')

            try:
                data = json.loads(statestore_redis.get(state))
            except Exception as e:
                logger.error(e)
                return render(request, self.template_name, {'chat_form': ChatForm(), 'phone_form': form, 'error': 'Invalid state'})

            scope = 'USER_PHONE'
            authorization_info = data.get(scope, {})

            # todo: check the expiry
            access_token = authorization_info.get('access_token')
            if access_token is None:
            # divar oauth fellow to get access_token
                params = {
                    'response_type' : 'code',
                    'client_id' : settings.DIVAR_APP_SLUG,
                    'redirect_uri' : settings.DIVAR_FALLBACK_REDIRECT_URL,
                    'scope' : scope,
                    'state' : f"{state}||{scope}",
                }
                redirect_uri = settings.DIVAL_OAUTH_REDIRECT_URL + f'?{urlencode(params)}'
                return redirect(redirect_uri)

            else:
                # send message in chat
                phone_service = PhoneService(x_api_key=settings.DIVAR_API_KEY, access_token=access_token)
                res = phone_service.show_phone()

                logger.info("Show phonenumber")
                logger.info(res)

                return render(request, self.template_name, {'chat_form': ChatForm(), 'phone_form': form, 'phone_numbers': res.get('phone_numbers', [])})
        else:
             render(request, self.template_name, {'chat_form': ChatForm(), 'phone_form': form})


