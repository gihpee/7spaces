from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import JSONField
from django.utils import timezone


class Applications(models.Model):
    phone_number = models.CharField(max_length=16)
    agent_fio = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    class Meta:
        app_label = 'platform_7s'


class Unit_Dubai(models.Model):
    unit_type = models.CharField(max_length=255)
    general = models.CharField(max_length=255)
    available_units = models.IntegerField(null=True, blank=True)
    price_min = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    price_max = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    size_min = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    size_max = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    psf_min = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    psf_max = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    floor_plan_image_links = JSONField(blank=True, null=True)
    num_bedrooms = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = 'platform_7s'


class Object_Dubai(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    sale_type = models.CharField(max_length=20)
    parking_spaces = models.CharField(max_length=3)
    down_price = models.DecimalField(max_digits=20, decimal_places=2)
    site = models.URLField(null=True, blank=True)
    longitude = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.CharField(max_length=20, null=True, blank=True)
    developer = models.CharField(max_length=255, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    logo_logo = models.URLField(null=True, blank=True)
    photo_url = models.URLField(null=True, blank=True)
    photo_logo = models.URLField(null=True, blank=True)
    construction_percent = models.CharField(max_length=20, null=True, blank=True)
    construction_inspection_date = models.CharField(max_length=255, null=True, blank=True)
    construction_percent_out_of_plan = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    transactions = JSONField(null=True, blank=True)
    total = JSONField(null=True, blank=True)
    apartments = JSONField(null=True, blank=True)
    start_at = models.CharField(max_length=255, null=True, blank=True)
    planned_at = models.CharField(max_length=255, null=True, blank=True)
    predicted_completion_at = models.CharField(max_length=255, null=True, blank=True)
    completed_at = models.CharField(max_length=255, null=True, blank=True)
    distance_to_city = models.CharField(max_length=20, null=True, blank=True)
    brochure = models.URLField(null=True, blank=True)
    overall_available_units = models.IntegerField(null=True, blank=True)
    album = JSONField(null=True, blank=True)
    facilities = ArrayField(models.CharField(max_length=255), blank=True, null=True, max_length=10)
    residential_complex_sale_status = models.CharField(max_length=255, null=True, blank=True)
    is_floor_plan_view = models.BooleanField(default=True)
    overall_min_unit_size = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    overall_max_unit_size = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    overall_min_unit_psf = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    overall_max_unit_psf = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    overall_min_unit_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    overall_max_unit_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    payment_plans = JSONField(blank=True, null=True)
    units = models.ManyToManyField(Unit_Dubai)

    class Meta:
        app_label = 'platform_7s'


class Unit_AbuDhabi(models.Model):
    unit_type = models.CharField(max_length=255)
    general = models.CharField(max_length=255)
    available_units = models.IntegerField(null=True, blank=True)
    price_min = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    price_max = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    size_min = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    size_max = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    psf_min = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    psf_max = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    floor_plan_image_links = JSONField(blank=True, null=True)
    num_bedrooms = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        app_label = 'platform_7s'


class Object_AbuDhabi(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    sale_type = models.CharField(max_length=20)
    parking_spaces = models.CharField(max_length=3)
    down_price = models.DecimalField(max_digits=20, decimal_places=2)
    site = models.URLField(null=True, blank=True)
    longitude = models.CharField(max_length=20, null=True, blank=True)
    latitude = models.CharField(max_length=20, null=True, blank=True)
    developer = models.CharField(max_length=255, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    logo_logo = models.URLField(null=True, blank=True)
    photo_url = models.URLField(null=True, blank=True)
    photo_logo = models.URLField(null=True, blank=True)
    construction_percent = models.CharField(max_length=20, null=True, blank=True)
    construction_inspection_date = models.CharField(max_length=255, null=True, blank=True)
    construction_percent_out_of_plan = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    transactions = JSONField(null=True, blank=True)
    total = JSONField(null=True, blank=True)
    apartments = JSONField(null=True, blank=True)
    start_at = models.CharField(max_length=255, null=True, blank=True)
    planned_at = models.CharField(max_length=255, null=True, blank=True)
    predicted_completion_at = models.CharField(max_length=255, null=True, blank=True)
    completed_at = models.CharField(max_length=255, null=True, blank=True)
    distance_to_city = models.CharField(max_length=20, null=True, blank=True)
    brochure = models.URLField(null=True, blank=True)
    overall_available_units = models.IntegerField(null=True, blank=True)
    album = JSONField(null=True, blank=True)
    facilities = ArrayField(models.CharField(max_length=255), blank=True, null=True, max_length=10)
    residential_complex_sale_status = models.CharField(max_length=255, null=True, blank=True)
    is_floor_plan_view = models.BooleanField(default=True)
    overall_min_unit_size = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    overall_max_unit_size = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    overall_min_unit_psf = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    overall_max_unit_psf = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    overall_min_unit_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    overall_max_unit_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    payment_plans = JSONField(blank=True, null=True)
    units = models.ManyToManyField(Unit_AbuDhabi)

    class Meta:
        app_label = 'platform_7s'


class Collection(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)
    objects_abudhabi = models.ManyToManyField(Object_AbuDhabi)
    objects_dubai = models.ManyToManyField(Object_Dubai)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'platform_7s'


class CollectionUnitsAbuDhabi(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit_AbuDhabi, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)


class CollectionUnitsDubai(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit_Dubai, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)


class Booking(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    passport_scan = models.FileField(upload_to='passport_scans/')
    status = models.CharField(max_length=100)
    units_abudhabi = models.ManyToManyField(Unit_AbuDhabi)
    units_dubai = models.ManyToManyField(Unit_Dubai)


class Subscribtion(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()