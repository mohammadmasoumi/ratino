import json
import logging

from django.views import View
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect

from misc.divar.oauth import OAuthService
from misc.clients.redis import statestore_redis

logger = logging.getLogger(__name__)


class OAuthView(View):

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        state_scope = request.GET.get('state')

        state, scope = state_scope.split('||')

        try:
            data = json.loads(statestore_redis.get(state))
        except Exception as e:
            logger.error(e)
            return HttpResponse(content='application/json', status=401)

        oauth_service = OAuthService(client_secret=settings.DIVAR_API_KEY, app_slug=settings.DIVAR_APP_SLUG)
        result = oauth_service.get_access_token(code=code)
        if result is None:
            logger.error(result)
            return HttpResponse(content='application/json', status=401)

        logger.info("========= OAUTH Result =========")
        logger.info(result)

        data.update({scope: result})
        statestore_redis.delete(state)
        statestore_redis.setex(name=state, time=60*60, value=json.dumps(data))

        return redirect(f"{settings.DOMAIN}/divar/home/success?state={state}")
    