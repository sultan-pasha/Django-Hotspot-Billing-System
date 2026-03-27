from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# # Create your models here.

class CustomUser(AbstractUser):
    PLAN_COICES = [
        ('daily','daily'),
        ('weekly','weekly'),
        ('monthly','monthly'),
    ]
    related_name = 'customer'
    plan = models.CharField(_("الخطه"), max_length=20, choices=PLAN_COICES, default='monthly')
    is_activated = models.BooleanField(_("نشط"), default=False)


from django.db import models

class RadCheck(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=64, unique=True)
    attribute = models.CharField(max_length=64, default='Cleartext-Password')
    op = models.CharField(max_length=2, default=':=')
    value = models.CharField(max_length=253)
    users = []
    class Meta:
        db_table = 'radcheck'
        managed = False  # عشان Django ما يحاولش يعمل migrate على الجدول
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.username
        
users = {
    ('','')
}
for i in RadCheck.objects.all():
    users.add((i.username, i.username))

# جدول الباقات
class Package(models.Model):
    name = models.CharField(max_length=50)
    download_speed = models.CharField(max_length=20)  # مثال: '2048k'
    upload_speed = models.CharField(max_length=20)    # مثال: '1024k'
    duration_days = models.PositiveIntegerField()     # مدة الباقة بالأيام

    def __str__(self):
        return f"{self.name} ({self.download_speed}/{self.upload_speed})"

class RadReply(models.Model):
    # packages = {
    #     ('','')
    # }
    # for i in Package.objects.all():
    #     packages.add((i.name, i.download_speed + '/' + i.upload_speed))

    username = models.CharField(max_length=255)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2, default=':=')
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'radreply'
        managed = False
        verbose_name = 'speed'
        verbose_name_plural = 'speeds'

    def __str__(self):
        return f"{self.username} - {self.attribute}"

def apply_speed_limits(user_package):
    if user_package.package:
        username = user_package.user.username
        package = user_package.package

        # حذف السرعات السابقة
        if RadReply.objects.filter(username=username).exists():
            print("deleting previous speeds")
            RadReply.objects.filter(username=username).filter(
                attribute__in=[
                    'WISPr-Bandwidth-Max-Down',
                    'WISPr-Bandwidth-Max-Up'
                ]
            ).delete()
        else:
            # إضافة السرعات الجديدة
            print("creating new speeds")
            RadReply.objects.bulk_create([
                RadReply(
                    username=username,
                    attribute='WISPr-Bandwidth-Max-Down',
                    op=':=',
                    value=str(int(package.download_speed) * 1000)  # من kbps إلى bps
                ),
                RadReply(
                    username=username,
                    attribute='WISPr-Bandwidth-Max-Up',
                    op=':=',
                    value=str(int(package.upload_speed) * 1000)
                ),
            ])
    else:
        pass

class Plan(models.Model):
    name = models.CharField(max_length=100)
    download_speed = models.CharField(max_length=20)  # مثال: '10M'
    upload_speed = models.CharField(max_length=20)    # مثال: '2M'
    session_timeout = models.IntegerField(null=True, blank=True)  # بالثواني

    def __str__(self):
        return self.name

class RadiusUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    def __str__(self):
        return self.username


# ربط المستخدم بالباقة
class UserPackage(models.Model):
    user = models.OneToOneField(RadCheck, on_delete=models.CASCADE, unique=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    limit_total_data = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.package:
            return f"{self.user.username} - {self.package.name}"
        else:
            return f"{self.user.username} - Max Speed"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        apply_speed_limits(self)
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if RadReply.objects.filter(username = self.user.username).exists():
            RadReply.objects.filter(username=self.user.username).delete()

# جدول استهلاك المستخدم من قاعدة RADIUS
class RadAcct(models.Model):
    radacctid = models.BigAutoField(primary_key=True)  # حدد المفتاح الأساسي الموجود فعليًا
    username = models.CharField(max_length=64)
    acctstarttime = models.DateTimeField(null=True)
    acctstoptime = models.DateTimeField(null=True)
    acctsessiontime = models.IntegerField(null=True)
    acctinputoctets = models.BigIntegerField(null=True)   # Download
    acctoutputoctets = models.BigIntegerField(null=True)  # Upload

    class Meta:
        db_table = 'radacct'
        managed = False

    def __str__(self):
        return self.username

    def total_data_mb(self):
        return ((self.acctinputoctets or 0) + (self.acctoutputoctets or 0)) / (1024 * 1024)

class Activeusers(models.Model):
    Raduser = models.OneToOneField(RadAcct, on_delete=models.CASCADE, primary_key=True)
    Radip  = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return self.Raduser.username

# وظيفة لحساب استهلاك مستخدم معين
