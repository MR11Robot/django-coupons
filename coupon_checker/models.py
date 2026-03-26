from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from urllib.parse import urlparse
import uuid
from django.utils.timezone import now




CHECK_STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
)

TEST_CHOICES = (
    ('valid', 'Valid'),
    ('invalid', 'Invalid'),
)

class Company(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=120)
    slug = models.SlugField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        
    def __str__(self):
        return self.name

class Coupon(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    code = models.CharField(max_length=200)  # إزالة unique=True
    company = models.ForeignKey('Company', related_name="coupons", on_delete=models.CASCADE, default=1)
    check_status = models.CharField(max_length=10, choices=CHECK_STATUS_CHOICES, default='active')
    store = models.ForeignKey('Store', related_name="coupons", on_delete=models.CASCADE)
    countries = models.ManyToManyField('Country', related_name="coupons")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['code', 'store'], name='unique_coupon_per_store'),
    ]

    def clean(self):
        if Coupon.objects.filter(code=self.code, store=self.store).exclude(id=self.id).exists():
            raise ValidationError({'code': "Coupon with this code already exists for this store."})
            
    def __str__(self):
        return f"{self.code} ({self.store.name}) - {self.store.website.name}"

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        self.full_clean() 
        super().save(*args, **kwargs)


class Country(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    code = models.CharField(max_length=3, unique=True) 
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name



class Store(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=120)
    slug = models.SlugField(blank=True)
    url = models.URLField()
    check_status = models.CharField(max_length=10, choices=CHECK_STATUS_CHOICES, default='active')
    website = models.ForeignKey('Website', related_name="stores", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'website'], name='unique_store_name_per_website'),
            models.UniqueConstraint(fields=['url', 'website'], name='unique_store_url_per_website'),
        ]

    def clean(self):
        if Store.objects.filter(name=self.name, website=self.website).exclude(id=self.id).exists():
            raise ValidationError({'name': "A store with this name already exists for this website."})

        if Store.objects.filter(url=self.url, website=self.website).exclude(id=self.id).exists():
            raise ValidationError({'url': "A store with this URL already exists for this website."})

        parsed_url = urlparse(self.url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValidationError({'url': "Please enter a valid URL with a proper scheme (http or https)."})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        self.full_clean() 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.website.name})"
    
    @property
    def count_coupon(self):
        return Coupon.objects.filter(store=self).count()
    
class Website(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    name = models.CharField(max_length=100, unique=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    url = models.URLField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = urlparse(self.url).netloc
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.name
    
    @property
    def store_count(self):
        return self.stores.count()

    @property
    def count(self):
        return Website.objects.count()
    
    @property
    def coupon_count(self):
        return Coupon.objects.filter(store__website=self).count()
    

    
class CouponReport(models.Model):
    STATUS_CHOICES = (
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
    )
    
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    coupon = models.ForeignKey('Coupon', related_name="reports", on_delete=models.CASCADE)
    discount = models.PositiveIntegerField(default=0)
    product_link = models.URLField(max_length=2048)
    last_check = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='valid')
    checked_country = models.ForeignKey('Country', related_name="reports", on_delete=models.CASCADE, default=1)

    def clean(self):
        today = now().date()

        if CouponReport.objects.filter(
            coupon=self.coupon,
            coupon__store=self.coupon.store,
            checked_country=self.checked_country,
            last_check__date=today
        ).exclude(id=self.id).exists():
            raise ValidationError({
                'coupon': "This coupon already has a report for this store in this country today."
            })

    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report for {self.coupon.code} - {self.coupon.store.name} in {self.checked_country.name}"