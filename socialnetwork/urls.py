from django.conf.urls import url, include
from socialnetwork import views as sn_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$', sn_views.index, name='home'),
    url(r'^follow_stream$', sn_views.follow_stream, name='follow_stream'),
    url(r'^add_post$', sn_views.add_post, name='add_post'),
    url(r'^add_comment$', sn_views.add_comment, name='add_comment'),
    url(r'^edit_profile$', sn_views.edit_profile, name='edit_profile'),
    url(r'^update_profile$', sn_views.update_profile, name='update_profile'),
    url(r'^update_photo$', sn_views.update_photo, name='update_photo'),
    url(r'^get_photo/(?P<id>\d+)$', sn_views.get_photo, name='get_photo'),
    url(r'^follow/(?P<id>\d+)$', sn_views.follow, name='follow'),
    url(r'^unfollow/(?P<id>\d+)$', sn_views.unfollow, name='unfollow'),
    url(r'^login$', auth_views.login, {'template_name':'login.html'}, name='login'),
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
    url(r'^profile$', sn_views.profile, name='profile'),
    url(r'^register$', sn_views.register, name='register'),
    url(r'^get-posts-json$', sn_views.get_posts_json, name='get-posts-json'),
    url(r'^get-posts-json-followers$', sn_views.get_posts_json_followers, name='get-posts-json-followers'),
    url(r'^get-posts-json-profile$', sn_views.get_posts_json_profile, name='get-posts-json-profile'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$',
        sn_views.confirm_registration, name='confirm'),
]
