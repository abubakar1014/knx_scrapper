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
        unique_together = ('company_name', 'phone_number')
    
    def __str__(self):
        return f"{self.company_name} {self.owner_name}"
    
class ScraperDetail(TimeStamped):
    country_name = models.CharField(max_length=500,  blank=True, null=True, default="N/A")
    count = models.PositiveIntegerField(null=True, blank=True, default=0)
    url = models.CharField(max_length=500,  blank=True, null=True, default="N/A")
    
    class Meta:
        unique_together = ('country_name', 'url')
    
    def __str__(self):
        return f"{self.country_name} - {self.count}"
    
class UrlCount(TimeStamped):
    count = models.PositiveIntegerField(null=True, blank=True, default=0)
    url = models.CharField(max_length=500,  blank=True, null=True, default="N/A")


class CompaniesData(TimeStamped):
    uid = models.CharField(max_length=255, default="N/A")
    id = models.AutoField(primary_key=True)
    salutation_id = models.IntegerField(default=0)
    stars = models.IntegerField(default=0)
    stars_feedback = models.IntegerField(default=0)
    stars_projects = models.IntegerField(default=0)
    stars_engagement = models.IntegerField(default=0)
    stars_tools = models.IntegerField(default=0)
    stars_knowledge = models.IntegerField(default=0)
    score_feedback = models.IntegerField(default=0)
    score_projects = models.IntegerField(default=0)
    score_engagement = models.IntegerField(default=0)
    score_tools = models.IntegerField(default=0)
    score_knowledge = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    visible = models.BooleanField(default=False)
    visible_list = models.BooleanField(default=False)
    visible_map = models.BooleanField(default=False)
    national_group_visible = models.BooleanField(default=False)
    username = models.CharField(max_length=255, default="N/A")
    firstname = models.CharField(max_length=255, default="N/A")
    lastname = models.CharField(max_length=255, default="N/A")
    company = models.CharField(max_length=255, default="N/A")
    phone = models.CharField(max_length=20, default="N/A")
    mobile = models.CharField(max_length=20, default="N/A")
    street = models.CharField(max_length=255, default="N/A")
    housenumber = models.CharField(max_length=10, default="N/A")
    zipcode = models.CharField(max_length=10, default="N/A")
    city = models.CharField(max_length=255, default="N/A")
    country_id = models.IntegerField(default=0)
    vat = models.CharField(max_length=20, default="N/A")
    email = models.EmailField(unique=True, default="N/A")
    website = models.URLField(default="N/A")
    language = models.CharField(max_length=10, default="N/A")
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)
    communication_journal = models.TextField(default="N/A")
    communication_journal_language_id = models.IntegerField(default=0)