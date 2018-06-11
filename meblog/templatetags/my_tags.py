
from django import template
from meblog import models
from django.db.models import Count

register = template.Library()


@register.inclusion_tag("archive.html")
def get_archive_tag(username):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    category_list = models.HomeCategory.objects.filter(blog=blog) \
        .annotate(c=Count("article")) \
        .values_list("title", 'c')

    tag_list = models.Tag.objects.filter(blog=blog). \
        annotate(n=Count("article")) \
        .values_list("title", "n")

    date_list = models.Article.objects.filter(user=user) \
        .extra(select={"time_tuple": "strftime('%%Y-%%m', create_time)"}).values("time_tuple") \
        .annotate(n=Count("nid")).values_list("time_tuple", "n")
    return {"category_list": category_list, "tag_list": tag_list, "date_list": date_list, 'username': username}




