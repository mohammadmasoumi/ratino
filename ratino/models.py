from django.db import models


class Rate(models.Model):
    supplier_id = models.ForeignKey('divar_homepage.DivarProfile', on_delete=models.CASCADE, related_name='supplier')
    demand_id = models.ForeignKey('divar_homepage.DivarProfile', on_delete=models.CASCADE, related_name='demand')
    post_token = models.CharField(max_length=50)
    text = models.CharField(max_length=255)
    rate = models.IntegerField(default=0)
