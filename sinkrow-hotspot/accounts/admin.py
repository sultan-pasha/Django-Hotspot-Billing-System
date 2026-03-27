# from .models import Plan, RadiusUser
from django.contrib import admin
from .models import Package, UserPackage, RadAcct, RadCheck, RadReply, Activeusers
from django.db.models import Sum
from datetime import timedelta, datetime
from django.utils import timezone

# # # app_name/admin.py

# # admin.site.register(RadiusUser) 
admin.site.register(Activeusers)

def get_user_usage_mb(username):
    usage = RadAcct.objects.filter(username=username).aggregate(
        total_download=Sum('acctinputoctets'),
        total_upload=Sum('acctoutputoctets')
    )
    total = (usage['total_download'] or 0) + (usage['total_upload'] or 0)
    return total / (1024 * 1024)  # إلى ميجابايت

# وظيفة تحقق من تجاوز الباقة

def is_user_over_limit(user_package):
    if not user_package.is_active:
        return True
    if user_package.package:
        usage = get_user_usage_mb(user_package.user.username)
        expired = user_package.start_date + timedelta(days=user_package.package.duration_days) < timezone.now()
        return usage >= user_package.package.data_limit_mb or expired

@admin.register(RadCheck)
class RadCheckAdmin(admin.ModelAdmin):
    list_display = ('username', 'attribute', 'op', 'value')
    search_fields = ('username',)

@admin.register(RadReply)
class RadReplyAdmin(admin.ModelAdmin):
    list_display = ('username', 'attribute', 'op', 'value')
    search_fields = ('username',)


# Admin Interfaces
@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'download_speed', 'upload_speed', 'duration_days')

class UserPackageAdmin(admin.ModelAdmin):
    list_display = ('user', 'package', 'start_date', 'is_active', 'usage_mb', 'expired')
    list_filter = ('is_active', 'package')  # فلترة حسب نوع الباقة أو التفعيل
    search_fields = ('user__username',)

    def usage_mb(self, obj):
        return f"{get_user_usage_mb(obj.user.username):.2f} MB"

    def expired(self, obj):
        if obj.package:
            return obj.start_date + timedelta(days=obj.package.duration_days) < timezone.now()
    def delete_queryset(self, request, queryset, *args, **kwargs):
        for obj in queryset:
            if RadReply.objects.filter(username = obj.user.username).exists():
                RadReply.objects.filter(username = obj.user.username).delete()
                obj.delete()
                print(f"Custom logic before deleting: {obj}")
            else:
                obj.delete()
admin.site.register(UserPackage, UserPackageAdmin)
@admin.register(RadAcct)
class RadAcctAdmin(admin.ModelAdmin):
    list_display = ('username', 'acctstarttime', 'acctstoptime', 'acctsessiontime', 'acctinputoctets', 'acctoutputoctets', 'total_data_mb_display')
    list_filter = ('username', )
    def total_data_mb_display(self, obj):
        return f"{obj.total_data_mb():.2f} MB"
    total_data_mb_display.short_description = 'Total Data (MB)'

