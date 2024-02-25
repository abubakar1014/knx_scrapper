from django.db import models
from knx.utils import TimeStamped

class ProfileData(TimeStamped):
    company_name = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=500, blank=True, null=True)
    country = models.CharField(max_length=500,  blank=True, null=True)
    owner_name = models.CharField(max_length=500,  blank=True, null=True)
    address = models.CharField(max_length=500,  blank=True, null=True)
    phone_number = models.CharField(max_length=500,  blank=True, null=True)
    mobile_number = models.CharField(max_length=500,  blank=True, null=True)
    website = models.CharField(max_length=500,  blank=True, null=True)
    email = models.CharField(max_length=500,  blank=True, null=True)
    location = models.CharField(max_length=500,  blank=True, null=True)

    class Meta:
        unique_together = ['address', 'phone_number']
    
    def __str__(self):
        return f"{self.company_name} {self.owner_name}"
    
class ScraperDetail(TimeStamped):
    count = models.CharField(max_length=20)