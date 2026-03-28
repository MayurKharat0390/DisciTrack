from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def assetlinks_view(request):
    data = [{
      "relation": ["delegate_permission/common.handle_all_urls"],
      "target": {
        "namespace": "android_app",
        "package_name": "app.vercel.grind_core.twa",
        "sha256_cert_fingerprints": ["73:DB:B7:03:82:93:96:A7:BC:64:25:74:23:60:64:D6:AF:70:13:E4:84:10:A8:AA:2F:65:8E:06:DC:25:81:17"]
      }
    }]
    return JsonResponse(data, safe=False)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('.well-known/assetlinks.json', assetlinks_view),
    path('accounts/', include('accounts.urls')),
    path('attendance/', include('attendance.urls')),
    path('goals/', include('goals.urls')),
    path('', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
