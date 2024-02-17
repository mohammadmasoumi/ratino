import convert_numbers
from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView

from divar_homepage.models import DivarProfile, Scope
from kenar.models.actions import LoadWebViewPage
from kenar.models.addon import Addon, StickyAddon
from kenar.models.widgets import ScoreRow
from ratino.models import Rate
from kenar.clients.addons import addons_client


# Create your views here.


class RateView(TemplateView):
    template_name = 'rate_form.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})

    def post(self, request, *args, **kwargs):
        score = int(request.POST.get('score'))
        text = request.POST.get('text')
        post_token = request.POST.get('post_token')
        demand_id = request.POST.get('demand_id')
        supplier_id = request.POST.get('supplier_id')
        supplier = DivarProfile.objects.get(pk=supplier_id)

        exists = Rate.objects.filter(demand_id=demand_id, supplier_id=supplier_id).exists()
        rate = Rate()
        if exists:
            rate = Rate.objects.filter(demand_id=demand_id, supplier_id=supplier_id).first()
        rate.rate = score
        rate.text = text
        rate.post_token = post_token
        rate.demand_id = DivarProfile.objects.get(pk=demand_id)
        rate.supplier_id = supplier
        rate.save()

        access_token = Scope.objects.filter(post_token=post_token).first().access_token
        sticky_addon = StickyAddon(
            widgets=[
                ScoreRow(
                    icon=None,
                    has_divider=True,
                    percentage_score=supplier.rate * 100 // 5,
                    title='امتیاز کاربران',
                    score_color=None,
                    action=LoadWebViewPage(settings.DOMAIN + '/rate/profile?id=' + supplier_id),
                )
            ],
            categories=[]
        )

        if supplier.addon_id:
            try:
                addons_client.delete_user_addon(user_addon_id=supplier.addon_id, api_key=settings.DIVAR_API_KEY,
                                                oauth_access_token=access_token)
            except:
                print("")
        addon_id = addons_client.create_sticky_user_verification_addon(phone=supplier.phone,
                                                                       api_key=settings.DIVAR_API_KEY,
                                                                       oauth_access_token=access_token,
                                                                       sticky_addon=sticky_addon, )
        supplier.addon_id = addon_id
        supplier.save()
        return DivarSchemeRedirect("divar:://home")


class DivarSchemeRedirect(HttpResponseRedirect):
    allowed_schemes = ['divar']


class ProfileView(TemplateView):
    template_name = 'profile_view.html'

    def get(self, request, *args, **kwargs):
        profile_id = request.GET.get("id")
        profile = DivarProfile.objects.get(pk=profile_id)
        rates = Rate.objects.filter(supplier_id=profile_id)
        return self.render_to_response(
            {
                "rate_list": rates,
                "profile": profile,
                'rate_count': convert_numbers.english_to_persian(rates.count()),
                "rate_percent": {
                    "1": {
                        "text": convert_numbers.english_to_persian(profile.rate_percent(1)),
                        "percent": profile.rate_percent(1),
                    },
                    "2": {
                        "text": convert_numbers.english_to_persian(profile.rate_percent(2)),
                        "percent": profile.rate_percent(2),
                    },
                    "3": {
                        "text": convert_numbers.english_to_persian(profile.rate_percent(3)),
                        "percent": profile.rate_percent(3),
                    },
                    "4": {
                        "text": convert_numbers.english_to_persian(profile.rate_percent(4)),
                        "percent": profile.rate_percent(4),
                    },
                    "5": {
                        "text": convert_numbers.english_to_persian(profile.rate_percent(5)),
                        "percent": profile.rate_percent(5),
                    },
                }
            })
