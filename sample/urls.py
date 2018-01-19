from django.conf.urls import url
from sample import views


urlpatterns = [
    url(r'^signup/$', views.SignUpView.as_view(), name='signup'),
    url(r'^ajax/validate_username/$', views.validate_username, name='validate_username'),
    url(r'^$', views.upload_file, name='fb2_converter'),
    url(r'^get/(\w+)/([0-9]+\.fb2)/$', views.get_file,name='get_file'),
]