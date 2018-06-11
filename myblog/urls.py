
from django.conf.urls import url, include
from django.contrib import admin
from meblog import views

from myblog import settings
from django.views.static import serve

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^reg/$', views.reg, name='reg'),
    url(r'^login/$', views.log_in, name='login'),
    url(r'^index/$', views.index, name='index'),
    url(r'^logout/$', views.log_out, name='logout'),
    url(r'^meblog/$', include('meblog.urls', namespace='meblog', app_name='mb')),
    url(r'^captcha/$', views.captcha, name='captcha'),
    url(r'thumbs/$', views.thumbs),
    url(r'comment/$', views.comment),
    # 文章详情页
    url(r'^^(?P<username>\w{3,})/p/(?P<article_id>\d+)\.html/$', views.article),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    # 博客个人站点
    url(r'^(?P<username>\w{3,})/$', views.blog_site, name='blog_site'),
    # 博客个人分类标签页
    url(r'^(?P<username>\w{3,})/(?P<conditions>cate|tag|date)/(?P<params>\w+-?\w+)/$', views.blog_site),
]

