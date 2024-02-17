import math

from IPython.core.display import Math
from django.db import models
from django.db.models import Sum, Avg

from ratino.models import Rate



class Scope(models.Model):
    name = models.CharField(max_length=255, unique=True)
    access_token = models.CharField(max_length=500, unique=True)
    post_token = models.CharField(max_length=500, unique=True)


class DivarProfile(models.Model):
    user_id = models.CharField(max_length=50, unique=True)  # user_id
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    addon_id = models.CharField(max_length=500 , null=True)

    @property
    def rate(self) -> int:
        rates = Rate.objects.filter(supplier_id=self.id)
        return int(rates.aggregate(Avg('rate'))['rate__avg'])

    def rate_percent(self, rate: int) -> int:
        rates = Rate.objects.filter(supplier_id=self.id)
        count = rates.count()
        related_rates_count = rates.filter(rate=rate).count()
        return related_rates_count*100//count
