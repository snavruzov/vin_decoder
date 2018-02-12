from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns

from vinapi.views import DecodeViewSet


decode_detail = DecodeViewSet.as_view({
    'get': 'decode'
})

urlpatterns = [
    re_path('^decode/(?P<vin>[A-Za-z0-9]{17})$', decode_detail, name='decode'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
